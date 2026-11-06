"""The committed results of corpus v1 rebuild from their inputs and render end to end."""

import json
from pathlib import Path

from leakseed.generate import read_manifest
from leakseed.report import build_summary, render_markdown
from leakseed.score import union_estimands

ROOT = Path(__file__).resolve().parents[1]
V1, RESULTS = ROOT / "corpus" / "v1", ROOT / "results" / "v1"


def _without_resampling(x):
    """A summary without the bootstrap's interval bounds, the only part that varies with n_boot."""
    if isinstance(x, dict):
        return {k: _without_resampling(v) for k, v in x.items() if k not in ("lo", "hi", "n_boot")}
    return [_without_resampling(v) for v in x] if isinstance(x, list) else x


def test_committed_results_rebuild_and_render():
    summary = build_summary(V1, RESULTS, n_boot=50)
    manifest = read_manifest(V1)
    pairs = len(manifest) // 2
    assert summary["oracle"]["agree"] == len(manifest) and not summary["oracle"]["disagree"]
    for tool in summary["tools"].values():
        primary = tool["primary"]
        assert primary["recall"]["n"] == primary["paired_site"]["n"] == pairs
        assert primary["paired_site"]["k"] <= primary["recall"]["k"]
    rebuilt = json.loads(json.dumps(summary, default=float, allow_nan=False))

    def refuse(token):
        raise AssertionError(f"{token} is not JSON")

    text = (RESULTS / "summary.json").read_text(encoding="utf-8")
    committed = json.loads(text, parse_constant=refuse)
    assert _without_resampling(rebuilt) == _without_resampling(committed)
    text = render_markdown(summary)
    for heading in ("## Headline", "## Coverage", "## Paired tool comparisons", "## Size of the"):
        assert heading in text


def test_any_linter_columns_are_each_an_or_over_tools():
    rows = [
        {"id": "a", "twin": "b", "label": "leak", "template": "t"},
        {"id": "b", "twin": "a", "label": "clean", "template": "t"},
    ]
    flags_both = {  # a rule on code the twins share
        "a": {"flagged": True, "exact": False, "either": False},
        "b": {"flagged": True, "exact": False, "either": False},
    }
    flags_leak = {
        "a": {"flagged": True, "exact": True, "either": True},
        "b": {"flagged": False, "exact": False, "either": False},
    }
    union = union_estimands(rows, [flags_both, flags_leak], n_boot=10)
    assert [union[m]["k"] for m in ("recall", "fpr", "paired", "paired_site")] == [1, 1, 1, 1]
