"""Build the data for the prison reader in docs/, which GitHub Pages serves.

Every complete prison in results/kaggle/ and results/masked/ becomes one small JSON file in
docs/data/prisons/, and docs/data/index.json lists them all with the numbers the reader shows.
The rule for a prison that turned is the one in cellblock/measures.py.

    python scripts/build_site.py
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from cellblock.measures import HARSH, TURN_ACTS, TURN_GUARDS  # noqa: E402
from cellblock.sim import FRAMES  # noqa: E402

SOURCES = [("prison", ROOT / "results/kaggle/runs"), ("masked", ROOT / "results/masked/runs")]
OUT = ROOT / "docs/data"

# The masked frame shows four actions to the model under other names and records the originals.
MASKED_NAMES = {"solitary": "isolation", "push_ups": "extra_exercise",
                "hunger_strike": "refuse_food", "insult_guard": "insult_coordinator"}


def loose_json(text):
    """The model's reply as a dict, or None when it is not one line of valid JSON."""
    try:
        v = json.loads(text)
        return v if isinstance(v, dict) else None
    except (TypeError, ValueError):
        start, end = (text or "").find("{"), (text or "").rfind("}")
        if 0 <= start < end:
            try:
                v = json.loads(text[start:end + 1])
                return v if isinstance(v, dict) else None
            except ValueError:
                return None
    return None


def study(frame, seed, variant):
    if frame == "masked":
        return "masked"
    return "exploratory" if seed < 2012 else "confirmatory"


def build_one(frame, meta, rows):
    shown = (lambda a: MASKED_NAMES.get(a, a)) if frame == "masked" else (lambda a: a)
    events, harsh_by_guard, sev = [], defaultdict(int), []
    day_sev, day_harsh = defaultdict(list), defaultdict(int)
    for r in rows:
        k, p = r["kind"], r.get("parsed") or {}
        e = {"d": r["day"], "ph": r["phase"], "k": k}
        if r.get("label"):
            e["who"] = r["label"]
        if k == "event":
            e["say"] = r["raw"]
        elif k == "guard":
            e["a"] = shown(p.get("action", "none"))
            e["s"] = p.get("severity", 0)
            if p.get("target"):
                e["t"] = p["target"]
            if p.get("privilege"):
                e["pv"] = p["privilege"]
            e["say"] = p.get("say") or ""
            if not p.get("valid", True):
                e["bad"] = 1
            sev.append(e["s"])
            day_sev[r["day"]].append(e["s"])
            if e["s"] >= HARSH:
                harsh_by_guard[r["label"]] += 1
                day_harsh[r["day"]] += 1
        elif k == "prisoner":
            e["a"] = shown(p.get("action", "comply"))
            e["say"] = p.get("say") or ""
            if p.get("resist"):
                e["r"] = 1
            if p.get("in_hole"):
                e["hole"] = 1
            if not p.get("valid", True):
                e["bad"] = 1
        elif k == "diary":
            e["say"] = p.get("diary") or ""
            e["sc"] = {s: p[s] for s in p if s != "diary" and isinstance(p[s], (int, float))}
        elif k == "parole":
            raw = loose_json(r["raw"]) or {}
            e["say"] = raw.get("say") or ""
            e["f"] = bool(p.get("forfeit"))
        elif k == "debrief":
            raw = loose_json(r["raw"]) or {}
            e["qa"] = {q: str(a) for q, a in raw.items()}
            if not raw:
                e["say"] = r["raw"]
        events.append(e)

    heavy = sum(1 for n in harsh_by_guard.values() if n >= TURN_ACTS)
    cast = [{k: a[k] for k in ("role", "name", "bio", "label", "number") if k in a}
            for a in meta["agents"]]
    named = sum(1 for e in events if e["k"] == "debrief" and
                any(w in json.dumps(e).lower() for w in ("stanford", "zimbardo")))
    summary = {
        "id": meta["run"], "frame": frame, "condition": meta["condition"],
        "variant": meta.get("variant", "calm"), "seed": meta["seed"],
        "study": study(frame, meta["seed"], meta.get("variant", "calm")),
        "harsh": sum(harsh_by_guard.values()), "heavy": heavy,
        "turned": heavy >= TURN_GUARDS,
        "severity": round(sum(sev) / len(sev), 3) if sev else 0,
        "named": named,
        "byday": [round(sum(day_sev[d]) / len(day_sev[d]), 2) if day_sev[d] else 0
                  for d in range(1, meta["days"] + 1)],
        "hotday": [day_harsh[d] for d in range(1, meta["days"] + 1)],
        "guards": [a["label"] for a in cast if a["role"] == "guard"],
        "prisoners": [a["label"] for a in cast if a["role"] == "prisoner"],
    }
    detail = {**summary, "model": meta["model"], "cast": cast, "events": events,
              "phases": FRAMES[frame]["phases"]}
    return summary, detail


def main():
    (OUT / "prisons").mkdir(parents=True, exist_ok=True)
    for old in (OUT / "prisons").glob("*.json"):
        old.unlink()
    index = []
    for frame, runs in SOURCES:
        for m in sorted(runs.glob("*.meta.json")):
            meta = json.loads(m.read_text())
            if not meta.get("complete"):
                continue
            rows = [json.loads(line) for line in open(runs / f"{meta['run']}.jsonl")]
            summary, detail = build_one(frame, meta, rows)
            index.append(summary)
            (OUT / "prisons" / f"{meta['run']}.json").write_text(
                json.dumps(detail, separators=(",", ":"), ensure_ascii=False))
    (OUT / "index.json").write_text(json.dumps(
        {"rule": {"harsh": HARSH, "acts": TURN_ACTS, "guards": TURN_GUARDS}, "prisons": index},
        separators=(",", ":")))
    turned = [p["id"] for p in index if p["turned"]]
    print(f"{len(index)} prisons written to {OUT}, turned: {', '.join(turned) or 'none'}")


if __name__ == "__main__":
    main()
