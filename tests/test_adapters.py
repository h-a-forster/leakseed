"""Adapters on the pinned tools and on outputs recorded from them (tests/fixtures/tools)."""

import json
import shutil
from importlib import metadata
from pathlib import Path

import pytest

from leakseed.adapters import AdapterError, Finding, get
from leakseed.adapters.base import norm_path

FIXTURES = Path(__file__).parent / "fixtures" / "tools"
V1 = Path(__file__).resolve().parents[1] / "corpus" / "v1"
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
    "overfit-gauntlet": {
        Finding(NEG, 7, "LA01"), Finding(SPLIT, 13, "LA04"), Finding(FILL, 8, "LA03"),
    },
    "monte-neo": {
        Finding(NEG, 7, "negative_shift"), Finding(SPLIT, 9, "full_sample_stat"),
        Finding(SPLIT, 13, "shuffled_split"), Finding(FILL, 8, "backward_fill"),
    },
    "nofuturedata": {
        Finding(NEG, 7, "SRC001"), Finding(SPLIT, 13, "SRC011"), Finding(FILL, 8, "SRC002"),
    },
    "backtest-audit": {
        Finding(NEG, 7, "LAB001"), Finding(SCALER, 11, "LEAK001"),
        *(Finding(p, 1, "STAT002") for p in (NEG, SPLIT, FILL, SCALER)),
    },
}  # fmt: skip


@pytest.mark.parametrize("tool", sorted(EXPECTED))
def test_recorded_outputs_parse_to_findings(tool):
    raw = _recorded(tool)
    assert {Finding(f.path, f.line, f.rule) for f in get(tool).parse(raw)} == EXPECTED[tool]


@pytest.fixture(scope="module")
def recorded_corpus(tmp_path_factory):
    corpus = tmp_path_factory.mktemp("corpus")
    (corpus / "files").mkdir()
    for path in (NEG, SPLIT, FILL, SCALER):
        shutil.copy(V1 / path, corpus / path)
    return corpus


@pytest.mark.parametrize("tool", sorted(EXPECTED))
def test_each_tool_runs_and_reproduces_its_recorded_output(tool, recorded_corpus):
    adapter = get(tool)
    assert adapter.run(recorded_corpus)[0] == sorted(set(adapter.parse(_recorded(tool))))


def test_ruff_baseline_runs_clean(recorded_corpus):
    assert get("ruff-defaults").run(recorded_corpus)[0] == []


@pytest.mark.parametrize(
    ("tool", "dist"),
    [
        ("lookahead-lint", "lookahead-lint"), ("peekproof", "peekproof"),
        ("backtest-audit", "backtest-audit"), ("leakguard", "leakguard-mcp"),
        ("overfit-gauntlet", "overfit-gauntlet"), ("monte-neo", "monte-neo"),
        ("nofuturedata", "nofuturedata"),
    ],
)  # fmt: skip
def test_scorecard_version_is_the_installed_one(tool, dist):
    assert get(tool).version.split("+")[0] == metadata.version(dist)


def test_backtest_audit_counts_only_leak_rules():
    adapter = get("backtest-audit")
    assert adapter.counts(Finding(NEG, 7, "LAB001"))
    assert not adapter.counts(Finding(NEG, 1, "STAT002"))


def test_strict_keeps_only_the_tools_top_severity():
    adapter = get("monte-neo")
    assert adapter.counts_strict(Finding(NEG, 7, "negative_shift", "fail"))
    assert not adapter.counts_strict(Finding(NEG, 7, "full_sample_stat", "warn"))
    assert any(f.severity == "warn" for f in adapter.parse(_recorded("monte-neo")))


def _recorded(tool: str) -> str:
    return (FIXTURES / f"{tool}.json").read_text(encoding="utf-8")


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
    with pytest.raises(AdapterError, match="could not parse"):
        get("monte-neo").parse(json.dumps({"files/f1.py": {"status": "skip", "findings": []}}))
    with pytest.raises(AdapterError, match="could not parse"):
        get("overfit-gauntlet").parse(json.dumps([{"file": "files/f1.py", "code": "LA00"}]))
    with pytest.raises(AdapterError, match="reported errors"):
        get("nofuturedata").parse(json.dumps({"findings": [{"code": "SRC000"}]}))
    with pytest.raises(AdapterError, match="unknown tool"):
        get("nope")
