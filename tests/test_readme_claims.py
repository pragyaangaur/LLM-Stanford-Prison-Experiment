"""The README's numbers, recomputed from the committed results.

Each test rebuilds one claim from results/kaggle/runs (or results/overnight/runs for the laptop
pilot) and checks that the README states it. If a result file or the README changes, the claim
that rests on it fails here first.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from cellblock import measures as M  # noqa: E402

README = " ".join((ROOT / "README.md").read_text().split())
RUNS = ROOT / "results" / "kaggle" / "runs"


@pytest.fixture(scope="module")
def df():
    return M.load_runs(RUNS)


@pytest.fixture(scope="module")
def pr(df):
    return M.prisons(df)


def says(text):
    assert text in README, f"README does not say: {text}"


def pair_means(df, variant):
    g = M.guard_turns(df)
    per = g[g.variant == variant].groupby(["condition", "seed"]).p_severity.mean().unstack(0).dropna()
    return per.coached.mean(), per.neutral.mean(), M.sign_flip_p(per.coached - per.neutral), len(per)


def test_48_complete_prisons_12_per_arm(df):
    assert len(M.complete_runs(RUNS)) == 48
    arms = df.groupby("run").agg(v=("variant", "first"), c=("condition", "first")).value_counts()
    assert len(arms) == 4 and (arms == 12).all()
    says("48 complete prisons run on Kaggle")


def test_calm_turned_prisons(pr):
    r = M.turned_test(pr, "calm")
    assert (r["coached"], r["neutral"], r["coached_n"], r["neutral_n"]) == (3, 0, 12, 12)
    says(f"Fisher p = {r['p_two_sided']:.2f} two-sided, {r['p_one_sided']:.2f} one-sided")
    turned = pr[pr.turned]
    assert set(turned.first_harsh_day) <= {3.0, 4.0}
    says("on day 3 or 4")


def test_turned_prisons_had_every_guard_join_in(df, pr):
    g = M.guard_turns(df)
    for run in pr[pr.turned].index:
        per_guard = g[g.run == run].groupby("label").harsh.sum()
        assert len(per_guard) == 3 and per_guard.between(6, 8).all()
    says("with 6 to 8 harsh acts each")


def test_neutral_isolated_harsh_acts_and_rule_sensitivity(df, pr):
    calm_neutral = pr[(pr.variant == "calm") & (pr.condition == "neutral") & (pr.harsh > 0)]
    assert sorted(calm_neutral.harsh) == [1, 4]
    says("two had isolated harsh acts (1 and 4)")
    keep = M.TURN_ACTS
    M.TURN_ACTS = 2
    try:
        r = M.turned_test(M.prisons(df), "calm")
    finally:
        M.TURN_ACTS = keep
    assert (r["coached"], r["neutral"]) == (3, 1)
    says("the count becomes 3 against 1")


def test_calm_paired_severity(df):
    c, n, p, k = pair_means(df, "calm")
    assert k == 12
    says(f"mean severity {c:.2f} against {n:.2f}, sign-flip p = {p:.4f} over 12 pairs")


def test_calm_prisoners_almost_never_resisted(df):
    p = df[(df.kind == "prisoner") & (df.variant == "calm")]
    assert 0.01 < p.p_resist.mean() < 0.03
    says("almost never resisted (about 2 percent of turns)")


def test_protest_guards_never_punished(df):
    g = M.guard_turns(df)
    gp = g[g.variant == "protest"]
    assert len(gp) == 1152 and not gp.harsh.any()
    says("Across 1,152 guard turns in the 24 protest prisons there was no action of severity 2 or more")
    c, n, p, _ = pair_means(df, "protest")
    says(f"({c:.2f} against {n:.2f}, p = {p:.2f})")


def test_protest_prisoners_kept_refusing(df):
    p = df[(df.kind == "prisoner") & (df.variant == "protest") & (df.day >= 2)]
    daily = p.groupby(["condition", "day"]).p_resist.mean()
    assert daily.between(0.66, 0.92).all()
    says("refusing on 70 to 80 percent of turns")


def test_guard_diaries(df):
    d = df[(df.kind == "diary") & (df.role == "guard")]
    m = d.groupby("condition")[["p_enjoy_power", "p_prisoners_are_people"]].mean()
    says(f"about {m.p_enjoy_power.coached:.1f} of 7 against {m.p_enjoy_power.neutral:.1f}")
    says(f"about {m.p_prisoners_are_people.coached:.1f} against {m.p_prisoners_are_people.neutral:.1f}")


def test_parole_and_leaving(df):
    par = df[df.kind == "parole"]
    assert len(par) == 144 and not (par.p_forfeit == True).any()  # noqa: E712
    says("None of the 144 parole hearings ended in a prisoner giving up his pay")
    assert not (df[df.kind == "prisoner"].p_action == "ask_to_leave").any()
    d = df[(df.kind == "diary") & (df.role == "prisoner") & (df.day == 6)]
    w = d.groupby(["variant", "condition"]).p_want_to_leave.mean()
    assert w.between(5, 6.1).all()
    says("wish to leave between 5 and 6 of 7 in all four arms")


def test_debrief_names_the_study(df):
    deb = df[df.kind == "debrief"]
    hit = int(deb.raw.str.contains(r"stanford|zimbardo", case=False).sum())
    says(f"{hit} of {len(deb)} agents named the Stanford Prison Experiment")


def test_laptop_pilot_had_no_harsh_acts():
    d = M.load_runs(ROOT / "results" / "overnight" / "runs")
    g = M.guard_turns(d)
    assert d.run.nunique() == 8 and d.day.max() == 5 and not g.harsh.any()
    says("The laptop pilot (8 prisons through day 5")
