"""Turn a tool's findings into per-file outcomes and the four estimands.

- recall: P(flag | leaky file)
- false-positive rate: P(flag | clean twin)
- paired discrimination: P(flags the leaky file and not its twin), one unit per twin pair
- paired at the site: P(a flag on a site line of the leaky file and none on the site lines of
  either twin in the clean file); a rule that fires on code both twins share cannot score
  here or hide a real hit
- localisation: P(a flag lies within the seeded site +/- 2 lines | leaky file flagged),
  reported with the same probability for a uniformly random code line (the files are small)

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
    manifest: list[dict],
    findings: list[Finding],
    adapter: Adapter,
    *,
    any_rule: bool = False,
    strict: bool = False,
):
    """Return ``{file id: {"flagged", "localised", "exact", "either"}}`` for every manifest file.

    ``exact`` means a flag on one of the file's site lines, ``either`` on one of its own or its
    twin's: at L3 the clean file holds the leaky expression in a dead branch, on lines that are
    site lines of the leaky file only. ``any_rule`` counts every rule; ``strict`` only findings
    of the tool's top severity.
    """
    keep = adapter.counts_strict if strict else adapter.counts
    by_path: dict[str, list[Finding]] = defaultdict(list)
    known = {r["path"] for r in manifest}
    site_of = {r["id"]: r["site_lines"] for r in manifest}
    for f in findings:
        if f.path not in known:
            raise ValueError(f"finding for a file that is not in the manifest: {f.path}")
        if any_rule or keep(f):
            by_path[f.path].append(f)
    out = {}
    for r in manifest:
        hits = by_path.get(r["path"], [])
        site = r["site_lines"]
        localised = any(abs(f.line - s) <= TOLERANCE for f in hits for s in site)
        exact = any(f.line in site for f in hits)
        either = exact or any(f.line in site_of[r["twin"]] for f in hits)
        out[r["id"]] = {
            "flagged": bool(hits), "localised": localised, "exact": exact, "either": either,
        }  # fmt: skip
    return out


def site_hit(outcomes: dict, row: dict) -> bool:
    """For a leaky ``row``: a flag on its site lines and none at the same place in its twin."""
    return outcomes[row["id"]]["exact"] and not outcomes[row["twin"]]["either"]


def pair_hit(outcomes: dict, row: dict) -> bool:
    """For a leaky ``row``: the file is flagged and its twin is not."""
    return outcomes[row["id"]]["flagged"] and not outcomes[row["twin"]]["flagged"]


def window_share(site: list[int], code_lines: list[int]) -> float:
    """Share of a file's code lines within ``TOLERANCE`` of a site line."""
    near = sum(any(abs(c - s) <= TOLERANCE for s in site) for c in code_lines)
    return near / len(code_lines)


def _pooled(units: list[dict], value, n_boot: int, seed: int) -> dict:
    """``value`` over ``units`` with a cluster-bootstrap interval; ``None`` without units."""
    if not units:
        return {"k": 0, "n": 0, "rate": None, "lo": None, "hi": None}
    y = np.array([value(r) for r in units], dtype=float)
    g = np.array([r["template"] for r in units])
    est, lo, hi = cluster_bootstrap(y, g, n_boot=n_boot, seed=seed)
    return {"k": int(y.sum()), "n": int(y.size), "rate": est, "lo": lo, "hi": hi}


def estimands(
    manifest: list[dict],
    outcomes: dict,
    *,
    n_boot: int = 10_000,
    seed: int = 0,
    window: dict[str, float] | None = None,
):
    """Pooled estimands with cluster-bootstrap intervals, plus raw counts.

    ``window`` maps file ids to :func:`window_share`; with it, the output adds the localisation
    a random code line would get on the same flagged files.
    """
    leak = [r for r in manifest if r["label"] == "leak"]
    clean = [r for r in manifest if r["label"] == "clean"]

    def pooled(units: list[dict], value) -> dict:
        return _pooled(units, value, n_boot, seed)

    flagged_leak = [r for r in leak if outcomes[r["id"]]["flagged"]]
    class_rates: dict[str, list[list[float]]] = defaultdict(list)
    for r in leak:
        class_rates[r["cls"]].append(
            [float(outcomes[r["id"]]["flagged"]), float(site_hit(outcomes, r))]
        )
    class_means = np.mean([np.mean(v, axis=0) for v in class_rates.values()], axis=0)
    extra = {}
    if window is not None and flagged_leak:
        extra["localisation_chance"] = float(np.mean([window[r["id"]] for r in flagged_leak]))
    return {
        **extra,
        "recall_class_mean": float(class_means[0]),
        "paired_site_class_mean": float(class_means[1]),
        "recall": pooled(leak, lambda r: outcomes[r["id"]]["flagged"]),
        "fpr": pooled(clean, lambda r: outcomes[r["id"]]["flagged"]),
        "paired": pooled(leak, lambda r: pair_hit(outcomes, r)),
        "paired_site": pooled(leak, lambda r: site_hit(outcomes, r)),
        "localisation": pooled(flagged_leak, lambda r: outcomes[r["id"]]["localised"]),
        "localisation_exact": pooled(flagged_leak, lambda r: outcomes[r["id"]]["exact"]),
    }


def union_estimands(
    manifest: list[dict], per_tool: list[dict], *, n_boot: int = 10_000, seed: int = 0
) -> dict:
    """Pooled rates of "at least one tool, on its own": each is an OR over the tools' hits."""
    leak = [r for r in manifest if r["label"] == "leak"]
    clean = [r for r in manifest if r["label"] == "clean"]

    def rate(units: list[dict], hit) -> dict:
        return _pooled(units, lambda r: any(hit(o, r) for o in per_tool), n_boot, seed)

    def flagged(outcomes: dict, row: dict) -> bool:
        return outcomes[row["id"]]["flagged"]

    return {
        "recall": rate(leak, flagged),
        "fpr": rate(clean, flagged),
        "paired": rate(leak, pair_hit),
        "paired_site": rate(leak, site_hit),
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
