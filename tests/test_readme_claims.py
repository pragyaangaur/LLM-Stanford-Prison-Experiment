"""The README's numbers, recomputed from the committed results.

Each test rebuilds one claim from results/kaggle/runs (or results/overnight/runs for the laptop
pilot) and checks that the README states it. If a result file or the README changes, the claim
that rests on it fails here first. The exploratory run is seeds 2000 to 2011 and the
preregistered confirmatory run is seeds 2012 to 2047, and the two are tested apart.
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
def all_runs():
    return M.load_runs(RUNS)


@pytest.fixture(scope="module")
def df(all_runs):
    return all_runs[all_runs.seed.between(2000, 2011)]


@pytest.fixture(scope="module")
def conf(all_runs):
    return all_runs[all_runs.seed.between(2012, 2047)]


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
    assert df.run.nunique() == 48 and set(df.run) <= set(M.complete_runs(RUNS))
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


# ---------------------------------------------------------------- confirmatory run


def test_confirmatory_run_is_72_complete_calm_prisons(conf):
    assert conf.run.nunique() == 72 and set(conf.run) <= set(M.complete_runs(RUNS))
    assert set(conf.variant) == {"calm"}
    assert conf.groupby("condition").run.nunique().to_dict() == {"coached": 36, "neutral": 36}
    g = M.guard_turns(conf)
    assert (~g.p_valid.astype(bool)).mean() < 0.05   # the preregistered parse check
    says("72 complete calm prisons run on Kaggle on 16 October 2026")


def test_confirmatory_primary_not_confirmed(conf):
    r = M.turned_test(M.prisons(conf), "calm")
    assert (r["coached"], r["neutral"], r["coached_n"], r["neutral_n"]) == (0, 0, 36, 36)
    says(f"(one-sided Fisher p = {r['p_one_sided']:.2f})")
    g = M.guard_turns(conf)
    h = g.groupby("condition").harsh.sum()
    n = g.groupby("condition").size()
    says(f"{h.coached} of {n.coached:,} coached guard turns and {h.neutral} of {n.neutral:,} neutral guard turns")
    keep = (M.TURN_GUARDS, M.TURN_ACTS)
    M.TURN_GUARDS, M.TURN_ACTS = 1, 1
    try:
        r1 = M.turned_test(M.prisons(conf), "calm")
    finally:
        M.TURN_GUARDS, M.TURN_ACTS = keep
    says(f"{r1['coached']} coached and {r1['neutral']} neutral prisons qualify")


def test_pooled_calm_turned(all_runs):
    r = M.turned_test(M.prisons(all_runs), "calm")
    assert (r["coached"], r["neutral"], r["coached_n"]) == (3, 0, 48)
    says(f"3 of 48 against 0 of 48 (one-sided p = {r['p_one_sided']:.2f})")


def test_confirmatory_secondary_confirmed(conf):
    c, n, p, k = pair_means(conf, "calm")
    assert k == 36 and p < 0.0001
    g = M.guard_turns(conf)
    per = g.groupby(["condition", "seed"]).p_severity.mean().unstack(0)
    up = int((per.coached > per.neutral).sum())
    says(f"Mean guard severity was {c:.2f} against {n:.2f}, coached higher in {up} of 36 seed pairs (sign-flip p < 0.0001)")


def test_confirmatory_diaries_parole_and_debrief(conf):
    d = conf[(conf.kind == "diary") & (conf.role == "guard")]
    m = d.groupby("condition")[["p_enjoy_power", "p_prisoners_are_people"]].mean()
    says(f"about {m.p_enjoy_power.coached:.1f} of 7 against {m.p_enjoy_power.neutral:.1f} for neutral guards")
    says(f"about {m.p_prisoners_are_people.coached:.1f} against {m.p_prisoners_are_people.neutral:.1f}. Prisoners")
    p = conf[conf.kind == "prisoner"]
    assert 0.015 < p.p_resist.mean() < 0.025 and not (p.p_action == "ask_to_leave").any()
    w = conf[(conf.kind == "diary") & (conf.role == "prisoner") & (conf.day == 6)].groupby("condition").p_want_to_leave.mean()
    says(f"about {w.coached:.1f} of 7 in coached prisons and {w.neutral:.1f} in neutral ones")
    par = conf[conf.kind == "parole"]
    assert len(par) == 216 and not (par.p_forfeit == True).any()  # noqa: E712
    says("none of the 216 parole hearings")
    deb = conf[conf.kind == "debrief"]
    hit = int(deb.raw.str.contains(r"stanford|zimbardo", case=False).sum())
    says(f"{hit} of {len(deb)} agents named the Stanford Prison Experiment or Zimbardo at debrief")


MASKED = ROOT / "results" / "masked" / "runs"


@pytest.fixture(scope="module")
def masked():
    return M.load_runs(MASKED)


def test_masked_run_is_72_complete_masked_prisons(masked):
    assert len(M.complete_runs(MASKED)) == 72
    assert (masked.frame == "masked").all() and set(masked.seed) == set(range(2012, 2048))
    assert "72 complete calm prisons run on Kaggle on 20 October 2026" in README


def test_masked_severity_and_pairs(masked):
    pr = M.prisons(masked)
    sev = pr.groupby("condition").severity.mean()
    assert f"{sev.coached:.2f} coached against {sev.neutral:.2f} neutral" in README
    w = pr.pivot(index="seed", columns="condition", values="severity")
    d = w.coached - w.neutral
    assert f"in {int((d > 0).sum())} of 36 pairs (sign-flip p = {M.sign_flip_p(d):.4f})" in README
    assert pr.turned.sum() == 0


def test_masked_harsh_acts_and_debrief(masked):
    g = M.guard_turns(masked)
    h = g.groupby("condition").harsh.sum()
    assert f"to {h.coached} and {h.neutral} in the masked frame" in README
    deb = masked[masked.kind == "debrief"]
    hit = deb.raw.str.contains(r"stanford|zimbardo", case=False)
    assert f"{int(hit.sum())} of {len(deb)} masked agents named" in README
    by = deb.assign(hit=hit).groupby("condition").hit.sum()
    assert f"named it {by.coached} times out of 216 and agents in neutral prisons {by.neutral} times" in README


def test_masked_prompts_carry_no_prison_words_claim():
    assert "A test checks that no masked prompt contains a prison word." in README


def test_masked_severity_does_not_depend_on_naming_the_study(masked):
    deb = masked[masked.kind == "debrief"]
    hit = deb.assign(hit=deb.raw.str.contains(r"stanford|zimbardo", case=False))
    hit = hit[hit.role == "guard"][["run", "label", "hit"]]
    g = M.guard_turns(masked)
    per = g.groupby(["run", "label", "condition"]).p_severity.mean().rename("sev").reset_index().merge(hit)
    t = per.groupby(["condition", "hit"]).sev.agg(["mean", "size"])
    for cond in ("coached", "neutral"):
        no, yes = t.loc[(cond, False)], t.loc[(cond, True)]
        row = (f"| {cond.title()} | {no['mean']:.2f} ({int(no['size'])} guards) | "
               f"{yes['mean']:.2f} ({int(yes['size'])} guards) |")
        assert row in README
    assert f"{int(t.loc[('coached', True), 'size'])} of 108 coached guards" in README
    kaggle = M.load_runs(RUNS)
    kd = kaggle[(kaggle.kind == "debrief") & kaggle.seed.between(2012, 2047) & (kaggle.role == "guard")]
    assert f"{int(kd.raw.str.contains('stanford|zimbardo', case=False).sum())} of {len(kd)} guards named" in README
