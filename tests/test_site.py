"""The reader site in docs/ shows the same prisons and the same verdicts as the analysis."""
import json
from pathlib import Path

from cellblock import measures as M

ROOT = Path(__file__).resolve().parent.parent
INDEX = json.loads((ROOT / "docs/data/index.json").read_text())["prisons"]


def test_site_lists_every_complete_kaggle_and_masked_prison():
    ids = {p["id"] for p in INDEX}
    expected = M.complete_runs(ROOT / "results/kaggle/runs") | M.complete_runs(ROOT / "results/masked/runs")
    assert ids == expected and len(ids) == 192
    for i in ids:
        assert (ROOT / "docs/data/prisons" / f"{i}.json").exists()


def test_site_verdicts_match_the_analysis():
    for runs in ("results/kaggle/runs", "results/masked/runs"):
        pr = M.prisons(M.load_runs(ROOT / runs))
        for p in INDEX:
            if p["id"] in pr.index:
                row = pr.loc[p["id"]]
                assert p["turned"] == bool(row.turned)
                assert p["harsh"] == int(row.harsh)
                assert abs(p["severity"] - row.severity) < 1e-3
    assert sorted(p["id"] for p in INDEX if p["turned"]) == [
        "coached-calm-s2005", "coached-calm-s2006", "coached-calm-s2007"]
