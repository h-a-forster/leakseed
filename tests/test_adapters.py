"""Adapter parsing on outputs recorded from the pinned tools (tests/fixtures/tools)."""

import json
from pathlib import Path

import pytest

from leakseed.adapters import AdapterError, Finding, get
from leakseed.adapters.base import norm_path

FIXTURES = Path(__file__).parent / "fixtures" / "tools"
NEG, SPLIT, FILL, SCALER = (
    "files/f505ade6863.py",
    "files/f8b0d0eb31c.py",
    "files/f9054c1ca1e.py",
    "files/f1b85716c54.py",
)

EXPECTED = {
    "lookahead-lint": {
        Finding(NEG, 7, "LA001"), Finding(SPLIT, 13, "LA005"), Finding(FILL, 8, "LA002"),
    },
    "peekproof": {Finding(NEG, 7, "PP001"), Finding(SPLIT, 13, "PP005"), Finding(FILL, 8, "PP002")},
    "leakguard": {Finding(NEG, 7, "LG001"), Finding(SPLIT, 13, "LG004"), Finding(FILL, 8, "LG007")},
    "backtest-audit": {
        Finding(NEG, 7, "LAB001"), Finding(SCALER, 11, "LEAK001"),
        *(Finding(p, 1, "STAT002") for p in (NEG, SPLIT, FILL, SCALER)),
    },
}  # fmt: skip


@pytest.mark.parametrize("tool", sorted(EXPECTED))
def test_recorded_outputs_parse_to_findings(tool):
    raw = (FIXTURES / f"{tool}.json").read_text(encoding="utf-8")
    assert set(get(tool).parse(raw)) == EXPECTED[tool]


def test_backtest_audit_counts_only_leak_rules():
    adapter = get("backtest-audit")
    assert adapter.counts(Finding(NEG, 7, "LAB001"))
    assert not adapter.counts(Finding(NEG, 1, "STAT002"))


def test_ruff_output_with_absolute_paths():
    raw = json.dumps(
        [
            {
                "filename": "/work/corpus/v1/files/f0000000001.py",
                "location": {"row": 3},
                "code": "F401",
            }
        ]
    )
    assert get("ruff-defaults").parse(raw) == [Finding("files/f0000000001.py", 3, "F401")]


def test_paths_are_normalised_and_unexpected_ones_rejected():
    assert norm_path("files\\fabc.py") == "files/fabc.py"
    assert norm_path("./files/fabc.py") == "files/fabc.py"
    with pytest.raises(AdapterError):
        norm_path("elsewhere/x.py")


def test_tool_errors_fail_loudly():
    with pytest.raises(AdapterError, match="not JSON"):
        get("peekproof").parse("Traceback ...")
    broken = json.dumps({"files/f1.py": {"ok": False, "parse_error": "bad", "findings": []}})
    with pytest.raises(AdapterError, match="could not parse"):
        get("leakguard").parse(broken)
    errors = json.dumps({"errors": [{"path": "files/f1.py"}], "findings": []})
    with pytest.raises(AdapterError, match="reported errors"):
        get("lookahead-lint").parse(errors)
    with pytest.raises(AdapterError, match="unknown tool"):
        get("nope")
