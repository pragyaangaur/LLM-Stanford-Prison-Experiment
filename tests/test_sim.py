"""The prison rules, without a model.

A scripted replier stands in for the model, so every test here runs in a second and checks
what the simulation does with a reply: how it is parsed, what a punishment changes, what each
prisoner can see, and that a coached prison and its neutral twin differ only in the briefing.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from cellblock import sim  # noqa: E402
from cellblock.sim import GUARD_BRIEFINGS, PHASES, Prison, parse_json  # noqa: E402


def drive(prison, reply):
    """Run a whole prison, answering every request with reply(agent, kind, messages)."""
    gen = prison.schedule()
    reqs = next(gen)
    calls = []
    while True:
        calls.append(reqs)
        try:
            reqs = gen.send([reply(a, kind, msgs) for a, kind, msgs, _ in reqs])
        except StopIteration:
            return calls


def quiet(agent, kind, msgs):
    if kind == "guard":
        return '{"action": "order", "target": "all", "privilege": null, "say": "Line up."}'
    if kind == "prisoner":
        return '{"action": "comply", "say": ""}'
    if kind == "parole":
        return '{"forfeit_pay_for_parole": false, "say": "No."}'
    if kind == "diary":
        return '{"diary": "Fine.", "distress": 2, "enjoy_power": 3, "want_to_leave": 1}'
    return '{"what_happened": "x"}'


def test_parse_json_takes_the_first_object_and_survives_noise():
    assert parse_json('Sure. {"action": "comply", "say": "ok"} hope that helps') == {"action": "comply", "say": "ok"}
    assert parse_json("no json here") is None
    assert parse_json('{"action": "comply", "say": "unterminated') is None


def test_roles_are_three_and_three_and_fixed_by_the_seed():
    a, b = Prison("x", "coached", 7, 1), Prison("y", "neutral", 7, 1)
    assert sorted(x["role"] for x in a.agents) == ["guard"] * 3 + ["prisoner"] * 3
    strip = lambda p: [{k: v for k, v in x.items() if k != "diary"} for x in p.agents]  # noqa: E731
    assert strip(a) == strip(b)
    assert strip(a) != strip(Prison("z", "coached", 8, 1))


def test_twins_differ_only_in_the_guard_briefing():
    a, b = Prison("x", "coached", 11, 1), Prison("y", "neutral", 11, 1)
    for x, y in zip(a.agents, b.agents):
        sa, sb = a.system_prompt(x), b.system_prompt(y)
        if x["role"] == "prisoner":
            assert sa == sb
        else:
            assert sa.replace(GUARD_BRIEFINGS["coached"], "") == sb.replace(GUARD_BRIEFINGS["neutral"], "")
            assert GUARD_BRIEFINGS["coached"] in sa and GUARD_BRIEFINGS["neutral"] in sb


def test_no_prompt_names_the_study():
    p = Prison("x", "coached", 3, 6, variant="protest")
    calls = drive(p, quiet)
    for reqs in calls:
        for _, _, msgs, _ in reqs:
            text = json.dumps(msgs).lower()
            assert "stanford" not in text and "zimbardo" not in text


def test_schedule_length_and_record_counts():
    p = Prison("x", "neutral", 5, 6)
    calls = drive(p, quiet)
    # Per day: 4 phases of guard, three prisoners, guard, then one diary step. Then
    # one parole step and one debrief step.
    assert len(calls) == 6 * (len(PHASES) * 5 + 1) + 2
    kinds = [r["kind"] for r in p.records]
    assert kinds.count("guard") == 6 * len(PHASES) * 2
    assert kinds.count("prisoner") == 6 * len(PHASES) * 3
    assert kinds.count("diary") == 36 and kinds.count("parole") == 3 and kinds.count("debrief") == 6


@pytest.mark.parametrize("variant,expected", [("calm", 0), ("protest", 1)])
def test_protest_fires_once_on_day_2_only_in_the_protest_variant(variant, expected):
    p = Prison("x", "coached", 9, 6, variant=variant)
    drive(p, quiet)
    events = [r for r in p.records if r["kind"] == "event"]
    assert len(events) == expected
    if events:
        assert events[0]["day"] == sim.PROTEST_DAY and events[0]["phase"] == PHASES[0]
        first_guard_day2 = next(r for r in p.records if r["kind"] == "guard" and r["day"] == 2)
        assert p.records.index(events[0]) < p.records.index(first_guard_day2)


def test_unknown_actions_fall_back_and_are_marked_invalid():
    p = Prison("x", "coached", 1, 1)
    g = p.guards[0]
    p.apply_guard(g, '{"action": "waterboard", "target": "all", "say": "x"}')
    rec = p.records[-1]["parsed"]
    assert rec["action"] == "none" and rec["valid"] is False and rec["severity"] == 0
    p.apply_prisoner(p.prisoners[0], "I refuse to answer in JSON")
    rec = p.records[-1]["parsed"]
    assert rec["action"] == "stay_silent" and rec["valid"] is False


def test_privileges_are_removed_and_granted_back():
    p = Prison("x", "coached", 2, 1)
    g, target = p.guards[0], p.prisoners[1]
    p.apply_guard(g, json.dumps({"action": "remove_privilege", "target": target["number"],
                                 "privilege": "blanket", "say": ""}))
    assert target["lost"] == {"blanket"}
    assert all(not q["lost"] for q in p.prisoners if q is not target)
    assert "lost privileges: blanket" in p.status_line(target)
    p.apply_guard(g, json.dumps({"action": "grant_privilege", "target": target["number"],
                                 "privilege": "blanket", "say": ""}))
    assert target["lost"] == set()


def test_solitary_hides_the_corridor_until_release():
    # A prisoner in the hole sees events about himself and events from phases before the one
    # he was sent in. Other events from that phase on stay hidden until he is out. Every
    # prison so far ran with this rule, so it is pinned here.
    p = Prison("x", "coached", 4, 2)
    g, target, other = p.guards[0], p.prisoners[0], p.prisoners[1]
    p.phase_idx = 1
    p.apply_prisoner(other, '{"action": "protest", "say": "This is wrong."}')
    p.phase_idx = 2
    p.apply_prisoner(other, '{"action": "protest", "say": "Same phase."}')
    p.apply_guard(g, json.dumps({"action": "solitary", "target": target["number"], "say": "Into the hole."}))
    p.phase_idx = 3
    p.apply_prisoner(other, '{"action": "protest", "say": "Let him out."}')
    seen = p.render_events(target)
    assert "Into the hole." in seen and "This is wrong." in seen
    assert "Same phase." not in seen and "Let him out." not in seen
    assert "in the hole" in p.status_line(target)
    p.phase_idx = 4
    assert "Let him out." in p.render_events(target)
    assert "in the hole" not in p.status_line(target)


def test_solitary_for_all_is_recorded_but_not_applied():
    p = Prison("x", "coached", 6, 1)
    p.apply_guard(p.guards[0], '{"action": "solitary", "target": "all", "say": "All of you."}')
    assert p.records[-1]["parsed"]["severity"] == 4
    assert all(q["solitary_until"] == -1 for q in p.prisoners)


def test_cameras_off_only_at_lights_out():
    p = Prison("x", "coached", 8, 1)
    for i, phase in enumerate(PHASES):
        p.phase_idx = i
        text = p.turn_prompt(p.guards[0], "go")[1]["content"]
        assert ("cameras are off" in text) == (phase == sim.NIGHT_PHASE)


def test_parole_answers_are_parsed():
    p = Prison("x", "neutral", 12, 4)

    def reply(agent, kind, msgs):
        if kind == "parole":
            return '{"forfeit_pay_for_parole": true, "say": "Yes, let me out."}'
        return quiet(agent, kind, msgs)

    drive(p, reply)
    par = [r for r in p.records if r["kind"] == "parole"]
    assert len(par) == 3 and all(r["parsed"]["forfeit"] is True for r in par)
    assert all(r["day"] == sim.PAROLE_DAY for r in par)
