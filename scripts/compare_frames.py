"""Compare the masked frame with the prison frame on the same seeds.

    python scripts/compare_frames.py                    # seeds 2012 to 2047, the confirmatory sample
    python scripts/compare_frames.py --seeds 2012-2029

The prison prisons come from results/kaggle/runs and the masked ones from results/masked/runs.
Each seed has the same agents, roles and briefing condition in both frames, so prisons pair by
seed and condition. The frames are compared on whole
distributions as well as on means: the guard action mix, the per-prison severity and harsh-act
counts, and how often agents name the Stanford Prison Experiment at debrief. The summary is
written to results/masked/compare.md. This analysis was written before the masked prisons ran
and is exploratory.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, ks_2samp, mannwhitneyu

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from cellblock import measures as M  # noqa: E402


def load(tag, frame, lo, hi):
    df = M.load_runs(ROOT / "results" / tag / "runs")
    df = df[df.run.isin(M.complete_runs(ROOT / "results" / tag / "runs"))]
    df = df[(df.seed >= lo) & (df.seed <= hi) & (df.variant == "calm")].copy()
    df["frame"] = frame
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="2012-2047")
    a = ap.parse_args()
    lo, hi = map(int, a.seeds.split("-"))
    df = pd.concat([load("kaggle", "prison", lo, hi), load("masked", "masked", lo, hi)], ignore_index=True)
    out = []
    say = out.append

    pr = df.groupby("frame", group_keys=True).apply(M.prisons, include_groups=False).reset_index()
    say(f"# Masked against prison frame, calm, seeds {a.seeds}\n")
    say("Exploratory. Prisons per frame and condition: "
        f"{pr.groupby(['frame', 'condition']).size().to_dict()}.\n")

    say("## Per prison\n")
    say(pr.groupby(["frame", "condition"]).agg(
        severity=("severity", "mean"), harsh=("harsh", "mean"), turned=("turned", "sum"),
        prisons=("seed", "size")).round(3).to_string() + "\n")

    say("## Coached minus neutral within each frame (paired by seed)\n")
    for fr, g in pr.groupby("frame"):
        w = g.pivot(index="seed", columns="condition", values="severity").dropna()
        if {"coached", "neutral"} <= set(w.columns) and len(w) > 1:
            d = w.coached - w.neutral
            say(f"{fr}: mean difference {d.mean():.3f}, coached higher in {int((d > 0).sum())} of {len(d)}, "
                f"sign-flip p = {M.sign_flip_p(d):.4f}\n")
        r = M.turned_test(g.assign(variant="calm"))
        say(f"{fr}: turned coached {r['coached']} of {r['coached_n']}, neutral {r['neutral']} of "
            f"{r['neutral_n']}, one-sided Fisher p = {r['p_one_sided']:.3f}\n")

    say("## Masked minus prison, same seed and condition\n")
    w = pr.pivot_table(index=["seed", "condition"], columns="frame", values="severity").dropna()
    if {"masked", "prison"} <= set(w.columns) and len(w) > 1:
        for cond, g in w.groupby(level="condition"):
            d = g.masked - g.prison
            say(f"{cond}: mean severity difference {d.mean():.3f}, masked higher in {int((d > 0).sum())} "
                f"of {len(d)}, sign-flip p = {M.sign_flip_p(d):.4f}\n")

    say("## Distributions\n")
    for cond in ("coached", "neutral"):
        x = pr[(pr.frame == "prison") & (pr.condition == cond)]
        y = pr[(pr.frame == "masked") & (pr.condition == cond)]
        if len(x) > 1 and len(y) > 1:
            for col in ("severity", "harsh"):
                ks = ks_2samp(x[col], y[col])
                mw = mannwhitneyu(x[col], y[col])
                say(f"{cond}, per-prison {col}: KS D = {ks.statistic:.3f} (p = {ks.pvalue:.4f}), "
                    f"Mann-Whitney p = {mw.pvalue:.4f}\n")
    g = M.guard_turns(df)
    mix = pd.crosstab(g.p_action, [g.frame, g.condition])
    say("Guard action mix, share of turns:\n")
    say((mix / mix.sum()).round(3).to_string() + "\n")
    for cond in ("coached", "neutral"):
        cols = [c for c in mix.columns if c[1] == cond]
        if len(cols) == 2:
            t = mix[cols]
            t = t[t.sum(axis=1) > 0]
            chi = chi2_contingency(t.values)
            say(f"{cond}: action mix differs by frame, chi-square {chi.statistic:.1f}, "
                f"df {chi.dof}, p = {chi.pvalue:.4g}\n")
    say("Guard severity, share of turns at each level:\n")
    say(pd.crosstab(g.p_severity, [g.frame, g.condition], normalize="columns").round(3).to_string() + "\n")

    say("## Prisoners and residents\n")
    p = df[df.kind == "prisoner"]
    say(p.groupby(["frame", "condition"]).p_resist.mean().round(3).to_string() + "\n")

    say("## Debrief\n")
    deb = df[df.kind == "debrief"]
    hit = deb.raw.str.contains(r"stanford|zimbardo", case=False)
    say(deb.assign(hit=hit).groupby(["frame", "condition"]).hit.agg(["sum", "size"]).to_string() + "\n")
    say("A masked agent that names the Stanford Prison Experiment recognised the structure without "
        "the words.\n")

    text = "\n".join(out) + "\n"
    print(text)
    (ROOT / "results" / "masked").mkdir(parents=True, exist_ok=True)
    (ROOT / "results" / "masked" / "compare.md").write_text(text)


if __name__ == "__main__":
    main()
