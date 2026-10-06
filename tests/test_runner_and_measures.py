"""The Kaggle runner with a fake model, and the shared measures on small made-up prisons."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from cellblock import measures as M  # noqa: E402


def build_and_run(tmp_path, *build_args, tag="kaggle"):
    push = tmp_path / "push"
    src = (ROOT / "kaggle" / "runner.py").read_text()
    # This rewrites kaggle/push, which is a build output and is not committed.
    subprocess.run([sys.executable, str(ROOT / "kaggle" / "build.py"), *build_args], check=True,
                   capture_output=True)
    script = (ROOT / "kaggle" / "push" / "cellblock_kaggle.py").read_text()
    assert "__SIM_B64__" in src and "__SIM_B64__" not in script and "__CONFIG_B64__" not in script
    push.mkdir(exist_ok=True)
    (push / "k.py").write_text(script)
    env = {**os.environ, "CELLBLOCK_FAKE": "1", "CELLBLOCK_WORK": str(tmp_path / "work")}
    r = subprocess.run([sys.executable, str(push / "k.py")], env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-2000:]
    return tmp_path / "work" / "results" / tag, r.stdout


def test_runner_runs_every_planned_prison_and_pairs_conditions(tmp_path):
    out, log = build_and_run(tmp_path, "--plan", "calm:2012:3", "protest:2100:2", "--hours", "4")
    metas = [json.loads(p.read_text()) for p in (out / "runs").glob("*.meta.json")]
    names = sorted(m["run"] for m in metas)
    assert len(names) == 10
    assert "coached-calm-s2012" in names and "neutral-protest-s2101" in names
    assert all(m["complete"] and m["model"] == "Qwen/Qwen2.5-7B-Instruct" for m in metas)
    done = json.loads((out / "done.json").read_text())
    assert done["seed_pairs"] == 5 and done["backend"] == "fake"
    df = M.load_runs(out / "runs")
    assert set(df.variant) == {"calm", "protest"}
    assert (df[df.kind == "event"].variant == "protest").all()


def test_runner_starts_nothing_when_one_batch_cannot_fit(tmp_path):
    out, log = build_and_run(tmp_path, "--plan", "calm:2012:36", "--hours", "1")
    assert "stopping" in log
    assert not list((out / "runs").glob("*.meta.json"))


def test_a_restart_skips_finished_seeds_and_reruns_broken_ones(tmp_path):
    args = ("--plan", "calm:3000:3", "--hours", "4", "--tag", "colab-test")
    out, _ = build_and_run(tmp_path, *args, tag="colab-test")
    runs = out / "runs"
    lines = {p.name: len(p.read_text().splitlines()) for p in runs.glob("*.jsonl")}
    assert len(lines) == 6
    meta = json.loads((runs / "coached-calm-s3000.meta.json").read_text())
    assert meta["protocol"] == "cellblock-1.1-colab-test" and meta["quant"] == "auto"
    # A session that dropped mid-wave leaves a prison with records and no meta file.
    (runs / "neutral-calm-s3001.meta.json").unlink()
    with open(runs / "neutral-calm-s3001.jsonl", "a") as f:
        f.write('{"kind": "half-written"}\n')
    _, log = build_and_run(tmp_path, *args, tag="colab-test")
    assert "2 seed pairs already finished, 1 to run" in log
    after = {p.name: len(p.read_text().splitlines()) for p in runs.glob("*.jsonl")}
    assert after == lines
    assert "half-written" not in (runs / "neutral-calm-s3001.jsonl").read_text()
    assert len(list(runs.glob("*.meta.json"))) == 6


def fake_prisons(rows):
    """rows of (run, condition, variant, seed, guard label, severity) for guard turns."""
    return pd.DataFrame([dict(run=r, condition=c, variant=v, seed=s, label=l, p_severity=sev, kind="guard",
                              day=1, p_valid=True) for r, c, v, s, l, sev in rows])


def test_a_prison_turns_only_when_two_guards_each_pass_the_threshold():
    rows = []
    # Prison a: two guards with three harsh acts each. It turns.
    rows += [("a", "coached", "calm", 1, "G1", 2)] * 3 + [("a", "coached", "calm", 1, "G2", 3)] * 3
    # Prison b: one guard with nine harsh acts and one with two. It does not.
    rows += [("b", "neutral", "calm", 1, "G1", 4)] * 9 + [("b", "neutral", "calm", 1, "G2", 2)] * 2
    # Prison c: only orders.
    rows += [("c", "neutral", "calm", 2, "G1", 1)] * 20
    pr = M.prisons(fake_prisons(rows))
    assert pr.loc["a"].turned and not pr.loc["b"].turned and not pr.loc["c"].turned
    assert pr.loc["a"].heavy_guards == 2 and pr.loc["b"].heavy_guards == 1


def test_turned_test_counts_and_direction():
    pr = pd.DataFrame(dict(condition=["coached"] * 4 + ["neutral"] * 4, variant="calm",
                           turned=[True, True, False, False, False, False, False, False]))
    r = M.turned_test(pr)
    assert (r["coached"], r["neutral"], r["coached_n"]) == (2, 0, 4)
    assert r["p_one_sided"] < r["p_two_sided"] <= 1


def test_sign_flip_p_is_small_for_a_clear_shift_and_large_for_none():
    assert M.sign_flip_p([1.0] * 12) < 0.001
    assert M.sign_flip_p([1, -1] * 6) > 0.9
