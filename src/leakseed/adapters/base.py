"""Common adapter machinery: run a linter once over a corpus and map its output to findings."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


class AdapterError(Exception):
    """A linter failed, could not be found, or produced output the adapter cannot read."""


@dataclass(frozen=True, order=True)
class Finding:
    path: str  # corpus-relative, forward slashes, e.g. "files/f0123456789.py"
    line: int
    rule: str


def norm_path(raw: str) -> str:
    """Normalise a tool's path to the corpus-relative ``files/<name>.py`` form."""
    p = raw.replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    if "files/" in p:
        p = "files/" + p.split("files/")[-1]
    if not p.startswith("files/") or not p.endswith(".py"):
        raise AdapterError(f"unexpected path in tool output: {raw!r}")
    return p


def executable(name: str) -> str:
    """Find a console script installed next to the running interpreter."""
    found = shutil.which(name, path=str(Path(sys.executable).parent))
    if found is None:
        raise AdapterError(f"{name} is not installed in this environment (uv sync --group tools)")
    return found


def run_tool(cmd: list[str], cwd: Path, ok_codes: tuple[int, ...]) -> str:
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1", NO_COLOR="1")
    proc = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", env=env, check=False
    )
    if proc.returncode not in ok_codes:
        raise AdapterError(
            f"{Path(cmd[0]).name} exited {proc.returncode}: {proc.stderr.strip()[:500]}"
        )
    return proc.stdout


class Adapter:
    """One linter. Subclasses set the class attributes and implement ``invoke`` and ``parse``."""

    name: str = ""
    package: str = ""
    version: str = ""
    #: Rules the tool documents as look-ahead or leakage rules; ``None`` means every rule.
    leak_rules: frozenset[str] | None = None

    def invoke(self, corpus: Path) -> str:
        raise NotImplementedError

    def parse(self, raw: str) -> list[Finding]:
        raise NotImplementedError

    def run(self, corpus: Path) -> tuple[list[Finding], str]:
        raw = self.invoke(Path(corpus))
        return sorted(set(self.parse(raw))), raw

    def counts(self, f: Finding) -> bool:
        return self.leak_rules is None or f.rule in self.leak_rules


def load_json(raw: str, tool: str):
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AdapterError(
            f"{tool}: output is not JSON ({exc}); first bytes: {raw[:200]!r}"
        ) from exc


def findings_to_jsonl(findings: list[Finding]) -> str:
    return "".join(json.dumps(asdict(f), sort_keys=True) + "\n" for f in findings)
