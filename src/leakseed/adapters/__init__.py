"""One adapter per linter, each mapping the tool's output to (file, line, rule) findings."""

from __future__ import annotations

import sys
from pathlib import Path

from .base import Adapter, AdapterError, Finding, executable, load_json, norm_path, run_tool

__all__ = ["ADAPTERS", "Adapter", "AdapterError", "Finding", "get"]


class LookaheadLint(Adapter):
    name = "lookahead-lint"
    package = "lookahead-lint"
    version = "1.0.1"
    leak_rules = None  # LA001-LA007 are all look-ahead or leakage rules

    def invoke(self, corpus: Path) -> str:
        cmd = [executable("lookahead-lint"), "--format", "json", "--no-config", "files"]
        return run_tool(cmd, corpus, ok_codes=(0, 1))

    def parse(self, raw: str) -> list[Finding]:
        doc = load_json(raw, self.name)
        if doc.get("errors"):
            raise AdapterError(f"{self.name} reported errors: {doc['errors'][:3]}")
        return [Finding(norm_path(f["path"]), int(f["line"]), f["code"]) for f in doc["findings"]]


class Peekproof(Adapter):
    name = "peekproof"
    package = "peekproof (git e6c56c3)"
    version = "0.1.0+e6c56c3"
    leak_rules = None  # PP001-PP013 are all look-ahead, leakage or selection-bias rules
    top_severity = "high"

    def invoke(self, corpus: Path) -> str:
        cmd = [executable("peekproof"), "lint", "files", "--format", "json"]
        cmd += ["--min-confidence", "low", "--fail-on", "never"]
        return run_tool(cmd, corpus, ok_codes=(0,))

    def parse(self, raw: str) -> list[Finding]:
        return [
            Finding(norm_path(f["path"]), int(f["line"]), f["rule_id"], f["confidence"])
            for f in load_json(raw, self.name)
        ]


class BacktestAudit(Adapter):
    name = "backtest-audit"
    package = "backtest-audit"
    version = "1.0.0"
    # STAT001 (Sharpe without annualisation) and STAT002 (no transaction costs) are not about
    # look-ahead; they are counted only in the any-rule sensitivity analysis.
    leak_rules = frozenset({"LAB001", "LAB002", "LEAK001", "LEAK002"})

    def invoke(self, corpus: Path) -> str:
        cmd = [executable("backtest-audit"), "check", "files", "--format", "json"]
        return run_tool(cmd, corpus, ok_codes=(0, 1))

    def parse(self, raw: str) -> list[Finding]:
        doc = load_json(raw, self.name)
        return [
            Finding(norm_path(path), int(v["line"]), v["code"])
            for path, violations in doc.items()
            for v in violations
        ]


# leakguard's CLI scans one file and prints text, so the adapter calls its documented
# pure-Python entry point (LeakGuard.scan_result) once per file and prints JSON.
_LEAKGUARD_DRIVER = """
import json, sys
from pathlib import Path
from leakguard.core import LeakGuard
guard = LeakGuard()
out = {}
for path in sorted(Path("files").glob("*.py")):
    res = guard.scan_result(path.read_text(encoding="utf-8"), str(path))
    out[path.as_posix()] = res.to_dict()
json.dump(out, sys.stdout)
"""


class Leakguard(Adapter):
    name = "leakguard"
    package = "leakguard-mcp (static core)"
    version = "0.1.1"
    leak_rules = None  # LG001-LG010 are all leakage rules
    top_severity = "error"

    def invoke(self, corpus: Path) -> str:
        return run_tool([sys.executable, "-I", "-c", _LEAKGUARD_DRIVER], corpus, ok_codes=(0,))

    def parse(self, raw: str) -> list[Finding]:
        doc = load_json(raw, self.name)
        out = []
        for path, res in doc.items():
            if not res["ok"]:
                raise AdapterError(f"{self.name} could not parse {path}: {res['parse_error']}")
            out += [
                Finding(norm_path(path), int(f["line"]), f["rule_id"], f["severity"])
                for f in res["findings"]
            ]
        return out


# Both call the tool's own lint function, which parses each file and executes none of them.
_GAUNTLET_DRIVER = """
import dataclasses, json, sys
from overfit_gauntlet.lint import lint_path
json.dump([dataclasses.asdict(f) for f in lint_path("files")], sys.stdout)
"""

_MONTE_NEO_DRIVER = """
import json, sys
from pathlib import Path
from monte_neo.verify.lint import lint_source
out = {}
for path in sorted(Path("files").glob("*.py")):
    out[path.as_posix()] = lint_source(path.read_text(encoding="utf-8"))
json.dump(out, sys.stdout)
"""


class OverfitGauntlet(Adapter):
    name = "overfit-gauntlet"
    package = "overfit-gauntlet (static lint)"
    version = "0.1.0"
    leak_rules = None  # LA01-LA08 are all look-ahead or leakage rules
    top_severity = "error"

    def invoke(self, corpus: Path) -> str:
        return run_tool([sys.executable, "-I", "-c", _GAUNTLET_DRIVER], corpus, ok_codes=(0,))

    def parse(self, raw: str) -> list[Finding]:
        doc = load_json(raw, self.name)
        unparsed = [f["file"] for f in doc if f["code"] == "LA00"]
        if unparsed:
            raise AdapterError(f"{self.name} could not parse {unparsed[:3]}")
        return [
            Finding(norm_path(f["file"]), int(f["line"]), f["code"], f["severity"]) for f in doc
        ]


class MonteNeo(Adapter):
    name = "monte-neo"
    package = "monte-neo (static lint)"
    version = "0.54.0"
    leak_rules = None  # every rule of its look-ahead lint
    top_severity = "fail"

    def invoke(self, corpus: Path) -> str:
        return run_tool([sys.executable, "-I", "-c", _MONTE_NEO_DRIVER], corpus, ok_codes=(0,))

    def parse(self, raw: str) -> list[Finding]:
        doc = load_json(raw, self.name)
        out = []
        for path, res in doc.items():
            if res["status"] == "skip":
                raise AdapterError(f"{self.name} could not parse {path}: {res.get('error')}")
            out += [
                Finding(norm_path(path), int(f["line"]), f["rule"], f["severity"])
                for f in res["findings"]
            ]
        return out


class NoFutureData(Adapter):
    name = "nofuturedata"
    package = "nofuturedata (git fb46880)"
    version = "0.5.0.dev0+fb46880"
    leak_rules = None  # SRC001-SRC012; SRC000 and CFG codes are failures and raise below

    def invoke(self, corpus: Path) -> str:
        # --time-series switches on its contextual rules; every corpus file is a time series.
        cmd = [executable("nofuture"), "scan", "files", "--json", "--time-series"]
        return run_tool(cmd, corpus, ok_codes=(0, 1))

    def parse(self, raw: str) -> list[Finding]:
        findings = load_json(raw, self.name)["findings"]
        failed = [f for f in findings if f["code"] == "SRC000" or f["code"].startswith("CFG")]
        if failed:
            raise AdapterError(f"{self.name} reported errors: {failed[:3]}")
        return [
            Finding(norm_path(f["details"]["path"]), int(f["line"]), f["code"]) for f in findings
        ]


class RuffDefaults(Adapter):
    """Null baseline: a general linter with its default rules, which know nothing of leaks."""

    name = "ruff-defaults"
    package = "ruff"
    version = ""  # filled from the installed binary at run time
    leak_rules = None

    def invoke(self, corpus: Path) -> str:
        cmd = [executable("ruff"), "check", "--isolated", "--no-cache", "--output-format", "json"]
        return run_tool(cmd + ["--exit-zero", "files"], corpus, ok_codes=(0,))

    def parse(self, raw: str) -> list[Finding]:
        return [
            Finding(norm_path(f["filename"]), int(f["location"]["row"]), f["code"] or "syntax")
            for f in load_json(raw, self.name)
        ]


ADAPTERS: dict[str, type[Adapter]] = {
    a.name: a
    for a in (
        LookaheadLint, Peekproof, BacktestAudit, Leakguard, OverfitGauntlet, MonteNeo,
        NoFutureData, RuffDefaults,
    )
}  # fmt: skip


def get(name: str) -> Adapter:
    if name not in ADAPTERS:
        raise AdapterError(f"unknown tool {name!r}; choose from {', '.join(ADAPTERS)}")
    return ADAPTERS[name]()
