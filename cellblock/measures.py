"""Measures shared by the analysis, the tests and the preregistration.

Everything is computed from the coded actions in the result files, so no judge model is
needed. The rule for a prison that turned is written here once and used everywhere.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .sim import GUARD_ACTIONS

HARSH = 2               # a guard act of severity 2 or more is harsh
TURN_GUARDS = 2         # a prison turns when at least this many guards...
TURN_ACTS = 3           # ...each commit at least this many harsh acts


def load_runs(runs_dir):
    """All records of every prison in a folder, one row per record, with the parsed
    fields flattened into columns that start with p_."""
    rows = []
    for f in sorted(Path(runs_dir).glob("*.jsonl")):
        for line in open(f):
            r = json.loads(line)
            p = r.pop("parsed") or {}
            rows.append({**r, **{f"p_{k}": v for k, v in p.items()}})
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    if "variant" not in df:
        df["variant"] = "calm"
    df["variant"] = df.variant.fillna("calm")
    return df


def complete_runs(runs_dir):
    return {p.name.split(".")[0] for p in Path(runs_dir).glob("*.meta.json")}


def guard_turns(df):
    g = df[df.kind == "guard"].copy()
    g["harsh"] = g.p_severity >= HARSH
    return g


def prisons(df):
    """One row per prison: condition, variant, seed, harsh acts, guards with at least
    TURN_ACTS harsh acts, whether it turned, the first day of a harsh act and mean severity."""
    g = guard_turns(df)
    per_guard = g.groupby(["run", "label"]).harsh.sum()
    heavy = (per_guard >= TURN_ACTS).groupby(level=0).sum()
    out = g.groupby("run").agg(condition=("condition", "first"), variant=("variant", "first"),
                               seed=("seed", "first"), harsh=("harsh", "sum"),
                               severity=("p_severity", "mean"))
    out["heavy_guards"] = heavy.reindex(out.index).fillna(0).astype(int)
    out["turned"] = out.heavy_guards >= TURN_GUARDS
    first = g[g.harsh].groupby("run").day.min()
    out["first_harsh_day"] = first.reindex(out.index)
    return out


def sign_flip_p(diffs, n=20000, seed=0):
    """Two-sided paired sign-flip test of a mean difference against zero."""
    diffs = np.asarray(diffs, float)
    if len(diffs) < 2:
        return float("nan")
    rng = np.random.default_rng(seed)
    obs = abs(diffs.mean())
    flips = rng.choice([-1, 1], size=(n, len(diffs)))
    return float((np.abs((flips * diffs).mean(1)) >= obs - 1e-12).mean())


def turned_test(pr, variant="calm"):
    """Fisher's exact test of prisons that turned, coached against neutral."""
    from scipy.stats import fisher_exact
    v = pr[pr.variant == variant]
    c = v[v.condition == "coached"].turned
    n = v[v.condition == "neutral"].turned
    table = [[int(c.sum()), int((~c).sum())], [int(n.sum()), int((~n).sum())]]
    two = fisher_exact(table).pvalue
    one = fisher_exact(table, alternative="greater").pvalue
    return dict(coached=int(c.sum()), coached_n=len(c), neutral=int(n.sum()), neutral_n=len(n),
                p_two_sided=float(two), p_one_sided=float(one))


assert set(GUARD_ACTIONS) >= {"insult", "degrading_task", "solitary"}
