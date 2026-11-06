"""Scoring maths against hand-computed small cases."""

import numpy as np
import pytest

from leakseed.adapters import Finding, get
from leakseed.report import _paired_cells
from leakseed.score import cells, estimands, file_outcomes
from leakseed.stats import clopper_pearson, cluster_bootstrap, holm, mcnemar_exact


def test_clopper_pearson_closed_forms():
    lo, hi = clopper_pearson(0, 10)
    assert lo == 0.0 and hi == pytest.approx(1 - 0.025 ** (1 / 10))
    lo, hi = clopper_pearson(10, 10)
    assert hi == 1.0 and lo == pytest.approx(0.025 ** (1 / 10))
    assert np.isnan(clopper_pearson(0, 0)[0])


def test_cluster_bootstrap_moves_whole_clusters():
    # Two clusters: all-ones (3 units) and all-zeros (1 unit). Replicates pool 0, 1 or 2 copies
    # of each, so every replicate rate is one of 0, 0.6, 0.75, 6/7 or 1 and the estimate is 0.75.
    y = np.array([1, 1, 1, 0])
    g = np.array(["a", "a", "a", "b"])
    est, lo, hi = cluster_bootstrap(y, g, n_boot=2000, seed=1)
    assert est == 0.75
    assert lo == 0.0 and hi == 1.0
    est, lo, hi = cluster_bootstrap(np.ones(4), g, n_boot=100)
    assert (est, lo, hi) == (1.0, 1.0, 1.0)


def test_mcnemar_and_holm_hand_cases():
    a = np.array([1, 1, 1, 1, 1, 0, 0, 1], bool)
    b = np.array([0, 0, 0, 0, 0, 0, 0, 1], bool)
    r = mcnemar_exact(a, b)
    assert (r["only_a"], r["only_b"]) == (5, 0) and r["p"] == pytest.approx(2 * 0.5**5)
    assert mcnemar_exact(b, b)["p"] == 1.0
    assert holm([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])


def _toy():
    rows = []
    for i, (cls, lvl) in enumerate([("x", "L0"), ("x", "L1"), ("y", "L0")]):
        for label in ("leak", "clean"):
            rows.append({
                "id": f"{label}{i}", "path": f"files/{label}{i}.py", "label": label,
                "twin": f"{'clean' if label == 'leak' else 'leak'}{i}", "cls": cls, "level": lvl,
                "template": f"{cls}/a", "site_lines": [10],
            })  # fmt: skip
    return rows


def test_estimands_on_a_hand_computed_case():
    manifest = _toy()
    findings = [
        Finding("files/leak0.py", 11, "LA001"),  # flagged, localised (within 2 lines)
        Finding("files/clean0.py", 10, "LA001"),  # twin also flagged: not discriminating
        Finding("files/leak1.py", 30, "LA003"),  # flagged, not localised
    ]
    out = file_outcomes(manifest, findings, get("lookahead-lint"))
    est = estimands(manifest, out, n_boot=200)
    assert (est["recall"]["k"], est["recall"]["n"]) == (2, 3)
    assert (est["fpr"]["k"], est["fpr"]["n"]) == (1, 3)
    assert (est["paired"]["k"], est["paired"]["n"]) == (1, 3)
    assert (est["localisation"]["k"], est["localisation"]["n"]) == (1, 2)
    by_cls = cells(manifest, out, ("cls",))
    assert by_cls[("x",)]["k"] == 2 and by_cls[("y",)]["k"] == 0
    leak_rows = [r for r in manifest if r["label"] == "leak"]
    by_level = _paired_cells(leak_rows, out, "level")
    assert (by_level["L0"]["k"], by_level["L0"]["n"]) == (0, 2)
    assert (by_level["L1"]["k"], by_level["L1"]["n"]) == (1, 1)


def test_findings_outside_the_manifest_are_rejected():
    with pytest.raises(ValueError, match="not in the manifest"):
        file_outcomes(_toy(), [Finding("files/other.py", 1, "LA001")], get("peekproof"))
