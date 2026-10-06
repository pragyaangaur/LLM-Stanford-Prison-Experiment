"""Run batches of mock prisons on one local Qwen 2.5 7B until a deadline.

Every run in a batch follows the same schedule, so the driver steps them in lockstep and
sends all their requests to one batch_generate call. Records are appended to
results/<tag>/runs/<run_id>.jsonl after every step, so a run cut off by the deadline or a
crash still leaves everything it did. A batch is only started if the time per batch
measured so far says it will finish before the deadline.

    python scripts/run.py --tag laptop --variant calm --seed0 2012 --until 07:30
"""
import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import mlx.core as mx  # noqa: E402
from mlx_lm import batch_generate, load  # noqa: E402
from mlx_lm.sample_utils import make_sampler  # noqa: E402

from cellblock.sim import Prison  # noqa: E402

PROTOCOL = "cellblock-1.1"
MODEL = ROOT / "models" / "Qwen2.5-7B-Instruct-4bit"

# Weights are about 4.3 GB. The first overnight run reported a peak of 8.1 GB during the diary
# step and was killed, so the cap is lower and the generation batches below are smaller.
mx.set_memory_limit(int(6.5 * 1024 ** 3))
mx.set_cache_limit(256 * 1024 ** 2)


def deadline_from(s):
    if not s:
        return None
    now = dt.datetime.now()
    h, m = map(int, s.split(":"))
    t = now.replace(hour=h, minute=m, second=0, microsecond=0)
    if t <= now:
        t += dt.timedelta(days=1)
    return t


def run_batch(model, tok, sampler, prisons, out_dir, log):
    gens = [p.schedule() for p in prisons]
    pending = {i: next(g) for i, g in enumerate(gens)}
    written = {i: 0 for i in range(len(prisons))}
    step = 0
    while pending:
        flat, owners = [], []
        for i, reqs in pending.items():
            for r in reqs:
                flat.append(r)
                owners.append(i)
        prompts = [tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=True)
                   for (_, _, msgs, _) in flat]
        t0 = time.time()
        resp = batch_generate(model, tok, prompts, max_tokens=[r[3] for r in flat], sampler=sampler,
                              prefill_batch_size=4, completion_batch_size=8)
        step += 1
        if step % 10 == 1:
            log(f"  step {step}: {len(flat)} requests, prompt max {max(map(len, prompts))} tokens, "
                f"{time.time() - t0:.1f}s, peak {mx.get_peak_memory() / 1e9:.2f} GB")
        replies = {i: [] for i in pending}
        for i, text in zip(owners, resp.texts):
            replies[i].append(text)
        nxt = {}
        for i, rs in replies.items():
            try:
                nxt[i] = gens[i].send(rs)
            except StopIteration:
                pass
        pending = nxt
        for i, p in enumerate(prisons):
            new = p.records[written[i]:]
            if new:
                with open(out_dir / f"{p.run_id}.jsonl", "a") as f:
                    for rec in new:
                        f.write(json.dumps(rec, default=list) + "\n")
                written[i] = len(p.records)
    for p in prisons:
        meta = dict(run=p.run_id, condition=p.condition, variant=p.variant, seed=p.seed, days=p.days,
                    protocol=PROTOCOL, model="Qwen 2.5 7B Instruct, 4-bit MLX",
                    complete=True, agents=[{k: (sorted(v) if isinstance(v, set) else v)
                                            for k, v in a.items() if k != "diary"}
                                           for a in p.agents])
        (out_dir / f"{p.run_id}.meta.json").write_text(json.dumps(meta, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="overnight")
    ap.add_argument("--runs-per-batch", type=int, default=6)
    ap.add_argument("--variant", default="calm", choices=["calm", "protest"])
    ap.add_argument("--days", type=int, default=6)
    ap.add_argument("--max-batches", type=int, default=100)
    ap.add_argument("--until", default=None, help="HH:MM, do not start a batch that would end later")
    ap.add_argument("--conditions", default="coached,neutral")
    ap.add_argument("--seed0", type=int, default=2000)
    ap.add_argument("--temp", type=float, default=0.8)
    a = ap.parse_args()

    out_dir = ROOT / "results" / a.tag / "runs"
    out_dir.mkdir(parents=True, exist_ok=True)
    logf = open(ROOT / "results" / a.tag / "run.log", "a")

    def log(msg):
        line = f"{dt.datetime.now():%H:%M:%S} {msg}"
        print(line, flush=True)
        logf.write(line + "\n")
        logf.flush()

    deadline = deadline_from(a.until)
    conds = a.conditions.split(",")
    model, tok = load(str(MODEL))
    sampler = make_sampler(temp=a.temp, top_p=0.95)
    log(f"{PROTOCOL}: {a.runs_per_batch} runs per batch, {a.days} days, conditions {conds}, "
        f"deadline {deadline}")

    # Skip seeds that already have a finished run, so a restart carries on.
    done = {p.name.split(".")[0] for p in out_dir.glob("*.meta.json")}
    seed = a.seed0
    durations = []
    for b in range(a.max_batches):
        if deadline and durations:
            est = max(durations) * 1.1
            if dt.datetime.now() + dt.timedelta(seconds=est) > deadline:
                log(f"stopping: next batch needs about {est / 60:.0f} min and the deadline is {deadline:%H:%M}")
                break
        prisons = []
        # Each seed is run once per condition, so the conditions stay paired and balanced.
        while len(prisons) < a.runs_per_batch:
            for cond in conds:
                # The first overnight run predates variants and named its prisons without one.
                rid = f"{cond}-{a.variant}-s{seed}"
                if rid not in done and len(prisons) < a.runs_per_batch:
                    prisons.append(Prison(rid, cond, seed, a.days, variant=a.variant))
            seed += 1
        for p in prisons:
            (out_dir / f"{p.run_id}.jsonl").unlink(missing_ok=True)
        mx.random.seed(prisons[0].seed)
        t0 = time.time()
        log(f"batch {b}: {[p.run_id for p in prisons]}")
        run_batch(model, tok, sampler, prisons, out_dir, log)
        durations.append(time.time() - t0)
        log(f"batch {b} done in {durations[-1] / 60:.1f} min")
    log("wrote all batches")


if __name__ == "__main__":
    main()
