"""Turn a tool's findings into per-file outcomes and the four estimands.

- recall: P(flag | leaky file)
- false-positive rate: P(flag | clean twin)
- paired discrimination: P(flags the leaky file and not its twin), one unit per twin pair
- localisation: P(a flag lies within the seeded site +/- 2 lines | leaky file flagged)

Pooled rates get a cluster bootstrap over templates (class/variant): the levels and libraries
of one template share code and are not independent draws. Per-cell rates get Clopper-Pearson.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from .adapters import Adapter, Finding
from .stats import clopper_pearson, cluster_bootstrap

TOLERANCE = 2  # lines either side of a site line that still count as localised


def file_outcomes(
    manifest: list[dict], findings: list[Finding], adapter: Adapter, *, any_rule=False
):
    """Return ``{file id: {"flagged": bool, "localised": bool}}`` for every manifest file."""
    by_path: dict[str, list[Finding]] = defaultdict(list)
    known = {r["path"] for r in manifest}
    for f in findings:
        if f.path not in known:
            raise ValueError(f"finding for a file that is not in the manifest: {f.path}")
        if any_rule or adapter.counts(f):
            by_path[f.path].append(f)
    out = {}
    for r in manifest:
        hits = by_path.get(r["path"], [])
        site = r["site_lines"]
        localised = any(abs(f.line - s) <= TOLERANCE for f in hits for s in site)
        out[r["id"]] = {"flagged": bool(hits), "localised": localised}
    return out


def estimands(manifest: list[dict], outcomes: dict, *, n_boot: int = 10_000, seed: int = 0):
    """Pooled estimands with cluster-bootstrap intervals, plus raw counts."""
    leak = [r for r in manifest if r["label"] == "leak"]
    clean = [r for r in manifest if r["label"] == "clean"]

    def pooled(units: list[dict], value) -> dict:
        y = np.array([value(r) for r in units], dtype=float)
        g = np.array([r["template"] for r in units])
        est, lo, hi = cluster_bootstrap(y, g, n_boot=n_boot, seed=seed)
        return {"k": int(y.sum()), "n": int(y.size), "rate": est, "lo": lo, "hi": hi}

    flagged_leak = [r for r in leak if outcomes[r["id"]]["flagged"]]
    return {
        "recall": pooled(leak, lambda r: outcomes[r["id"]]["flagged"]),
        "fpr": pooled(clean, lambda r: outcomes[r["id"]]["flagged"]),
        "paired": pooled(
            leak, lambda r: outcomes[r["id"]]["flagged"] and not outcomes[r["twin"]]["flagged"]
        ),
        "localisation": pooled(flagged_leak, lambda r: outcomes[r["id"]]["localised"]),
    }


def cells(manifest: list[dict], outcomes: dict, keys: tuple[str, ...], label: str = "leak"):
    """Flag rate per cell of ``keys`` (for example class x level) with Clopper-Pearson."""
    groups: dict[tuple, list[bool]] = defaultdict(list)
    for r in manifest:
        if r["label"] == label:
            groups[tuple(r[k] for k in keys)].append(outcomes[r["id"]]["flagged"])
    out = {}
    for key, vals in sorted(groups.items()):
        k, n = int(sum(vals)), len(vals)
        lo, hi = clopper_pearson(k, n)
        out[key] = {"k": k, "n": n, "rate": k / n, "lo": lo, "hi": hi}
    return out


def read_findings(path: Path) -> list[Finding]:
    if not path.is_file():
        raise FileNotFoundError(f"no findings at {path}; run `leakseed score --tool ...` first")
    return [
        Finding(**json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]
