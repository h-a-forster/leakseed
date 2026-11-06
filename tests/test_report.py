"""The committed results of corpus v1 rebuild and render end to end."""

from pathlib import Path

from leakseed.generate import read_manifest
from leakseed.report import build_summary, render_markdown

ROOT = Path(__file__).resolve().parents[1]
V1, RESULTS = ROOT / "corpus" / "v1", ROOT / "results" / "v1"


def test_committed_results_rebuild_and_render():
    summary = build_summary(V1, RESULTS, n_boot=50)
    manifest = read_manifest(V1)
    pairs = len(manifest) // 2
    assert summary["oracle"]["agree"] == len(manifest) and not summary["oracle"]["disagree"]
    assert summary["tools"]["ruff-defaults"]["primary"]["recall"]["k"] == 0
    for tool in summary["tools"].values():
        primary = tool["primary"]
        assert primary["recall"]["n"] == primary["paired_site"]["n"] == pairs
        assert primary["paired_site"]["k"] <= primary["recall"]["k"]
    # L3 is built so that no syntactic rule can separate the twins.
    for tool in summary["tools"].values():
        assert tool["paired_site_by_level"]["L3"]["k"] == 0
    text = render_markdown(summary)
    for heading in ("## Headline", "## Coverage", "## Paired tool comparisons", "## Size of the"):
        assert heading in text
