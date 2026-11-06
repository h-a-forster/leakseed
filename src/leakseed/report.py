"""Scorecard: combine the manifest, oracle verdicts and every tool's findings."""

from __future__ import annotations

import itertools
import json
from collections import Counter
from pathlib import Path

from .adapters import ADAPTERS, get
from .generate import VERSION_FILE, read_manifest
from .score import cells, estimands, file_outcomes, read_findings
from .stats import clopper_pearson, holm, mcnemar_exact
from .templates import CLASSES, LEVELS, LIBS

BASELINE = "ruff-defaults"


def _fmt(e: dict) -> str:
    if e["n"] == 0:
        return "n/a (0 files)"
    return f"{100 * e['rate']:.1f}% [{100 * e['lo']:.1f}, {100 * e['hi']:.1f}] ({e['k']}/{e['n']})"


def build_summary(corpus: Path, results: Path, *, n_boot: int = 10_000, seed: int = 0) -> dict:
    manifest = read_manifest(corpus)
    version = json.loads((corpus / VERSION_FILE).read_text(encoding="utf-8"))
    oracle_path = results / "oracle.jsonl"
    if not oracle_path.is_file():
        raise FileNotFoundError(f"no {oracle_path}; run `leakseed verify` first")
    verdicts = [json.loads(x) for x in oracle_path.read_text(encoding="utf-8").splitlines() if x]
    by_id = {v["id"]: v for v in verdicts}
    if set(by_id) != {r["id"] for r in manifest}:
        raise ValueError("oracle verdicts do not cover exactly the manifest files")
    disagree = [v["id"] for v in verdicts if v["verdict"] != v["label"]]
    by_path = {r["path"]: r for r in manifest}
    leak_rows = [r for r in manifest if r["label"] == "leak"]

    tools_meta = json.loads((results / "tools.json").read_text(encoding="utf-8"))
    tools: dict[str, dict] = {}
    outcomes_by_tool: dict[str, dict] = {}
    for name in ADAPTERS:
        adapter = get(name)
        findings = read_findings(results / "findings" / f"{name}.jsonl")
        primary = file_outcomes(manifest, findings, adapter)
        anyrule = file_outcomes(manifest, findings, adapter, any_rule=True)
        outcomes_by_tool[name] = primary
        tools[name] = {
            "version": tools_meta[name]["version"],
            "leak_rules": sorted(adapter.leak_rules) if adapter.leak_rules else "all",
            "findings": len(findings),
            "rules_seen": dict(Counter(f.rule for f in findings).most_common()),
            "primary": estimands(manifest, primary, n_boot=n_boot, seed=seed),
            "any_rule": estimands(manifest, anyrule, n_boot=n_boot, seed=seed),
            "by_level": _cells(manifest, primary, ("level",)),
            "paired_by_level": _paired_cells(leak_rows, primary, "level"),
            "by_lib": _cells(manifest, primary, ("lib",)),
            "by_class": _cells(manifest, primary, ("cls",)),
            "fpr_by_class": _cells(manifest, primary, ("cls",), label="clean"),
            "by_class_level": _cells(manifest, primary, ("cls", "level")),
        }

    linters = [n for n in ADAPTERS if n != BASELINE]
    tests = []
    for a, b in itertools.combinations(linters, 2):
        oa, ob = outcomes_by_tool[a], outcomes_by_tool[b]
        rec_a = [oa[r["id"]]["flagged"] for r in leak_rows]
        rec_b = [ob[r["id"]]["flagged"] for r in leak_rows]
        tests.append({"a": a, "b": b, "measure": "recall", **mcnemar_exact(rec_a, rec_b)})
        pair_a = [oa[r["id"]]["flagged"] and not oa[r["twin"]]["flagged"] for r in leak_rows]
        pair_b = [ob[r["id"]]["flagged"] and not ob[r["twin"]]["flagged"] for r in leak_rows]
        tests.append({"a": a, "b": b, "measure": "paired", **mcnemar_exact(pair_a, pair_b)})
    for t, p in zip(tests, holm([t["p"] for t in tests]), strict=True):
        t["p_holm"] = p

    caught = {
        cls: {
            lvl: any(
                outcomes_by_tool[t][r["id"]]["flagged"]
                for t in linters
                for r in leak_rows
                if r["cls"] == cls and r["level"] == lvl
            )
            for lvl in LEVELS
        }
        for cls in CLASSES
    }
    union = {
        r["id"]: any(outcomes_by_tool[t][r["id"]]["flagged"] for t in linters) for r in manifest
    }
    union_est = estimands(
        manifest, {i: {"flagged": f, "localised": False} for i, f in union.items()}, n_boot=n_boot
    )

    fps = []
    for name in linters:
        adapter = get(name)
        for f in read_findings(results / "findings" / f"{name}.jsonl"):
            r = by_path[f.path]
            if r["label"] == "clean" and adapter.counts(f):
                fps.append({"tool": name, "file": f.path, "line": f.line, "rule": f.rule,
                            "cls": r["cls"], "level": r["level"], "lib": r["lib"]})  # fmt: skip
    missed_l0 = [
        {"file": r["path"], "lines": r["site_lines"], "cls": r["cls"], "lib": r["lib"]}
        for r in leak_rows
        if r["level"] == "L0" and not union[r["id"]]
    ]
    witness_modes = Counter(
        by_id[r["id"]]["witness"]["mode"] for r in leak_rows if by_id[r["id"]]["witness"]
    )
    return {
        "corpus": {
            **version,
            "pairs": len(leak_rows),
            "templates": len({r["template"] for r in manifest}),
            "levels": list(LEVELS),
            "libs": list(LIBS),
        },
        "oracle": {
            **json.loads((results / "oracle_meta.json").read_text(encoding="utf-8")),
            "agree": len(verdicts) - len(disagree),
            "total": len(verdicts),
            "disagree": disagree,
            "runs": sum(v["runs"] for v in verdicts),
            "leak_witness_modes": dict(witness_modes),
        },
        "bootstrap": {"n_boot": n_boot, "seed": seed, "cluster": "template (class/variant)"},
        "tools": tools,
        "union": union_est,
        "mcnemar": tests,
        "coverage": {
            "caught": caught,
            "uncaught_classes": [c for c, lv in caught.items() if not any(lv.values())],
        },
        "false_positives": fps,
        "missed_l0": missed_l0,
    }


def _paired_cells(leak_rows, outcomes, key):
    """Paired discrimination per value of ``key``, with Clopper-Pearson."""
    out = {}
    for value in sorted({r[key] for r in leak_rows}):
        rows = [r for r in leak_rows if r[key] == value]
        k = sum(outcomes[r["id"]]["flagged"] and not outcomes[r["twin"]]["flagged"] for r in rows)
        lo, hi = clopper_pearson(k, len(rows))
        out[value] = {"k": k, "n": len(rows), "rate": k / len(rows), "lo": lo, "hi": hi}
    return out


def _cells(manifest, outcomes, keys, label="leak"):
    return {"/".join(k): v for k, v in cells(manifest, outcomes, keys, label).items()}


def _shade(rate: float) -> str:
    return (
        " "
        if rate == 0
        else "░"
        if rate < 0.25
        else "▒"
        if rate < 0.5
        else "▓"
        if rate < 0.75
        else "█"
    )


def render_markdown(s: dict) -> str:
    tools = list(s["tools"])
    linters = [t for t in tools if t != BASELINE]
    out = [f"# Scorecard (corpus seed {s['corpus']['seed']})", ""]
    o = s["oracle"]
    out.append(
        f"Corpus: {s['corpus']['files']} files = {s['corpus']['pairs']} leak/clean pairs, "
        f"{len(CLASSES)} classes, {s['corpus']['templates']} templates. Oracle: {o['agree']}/"
        f"{o['total']} labels confirmed ({o['runs']} script runs, n = {o['n']} rows, "
        f"{o['n_t']} cut points x {len(o['modes'])} perturbation modes)."
    )
    out.append(
        "Intervals: pooled rates use a cluster bootstrap over templates "
        f"({s['bootstrap']['n_boot']} resamples, percentile 95%); per-cell rates use "
        "Clopper-Pearson 95%."
    )
    out += ["", "## Headline (each tool's documented leakage rules)", ""]
    out.append(
        "| Tool | Version | Recall | False-positive rate | Paired discrimination | Localisation |"
    )
    out.append("|---|---|---|---|---|---|")
    for t in tools:
        p = s["tools"][t]["primary"]
        out.append(
            f"| {t} | {s['tools'][t]['version']} | {_fmt(p['recall'])} | {_fmt(p['fpr'])} | "
            f"{_fmt(p['paired'])} | {_fmt(p['localisation'])} |"
        )
    u = s["union"]
    out.append(
        f"| any of the four linters | - | {_fmt(u['recall'])} | {_fmt(u['fpr'])} | "
        f"{_fmt(u['paired'])} | - |"
    )
    out += ["", "## Sensitivity: every rule counts", ""]
    out.append("| Tool | Recall | False-positive rate | Paired discrimination |")
    out.append("|---|---|---|---|")
    for t in tools:
        p = s["tools"][t]["any_rule"]
        out.append(f"| {t} | {_fmt(p['recall'])} | {_fmt(p['fpr'])} | {_fmt(p['paired'])} |")

    out += ["", "## Recall by obfuscation level (Clopper-Pearson)", ""]
    out.append("| Tool | " + " | ".join(LEVELS) + " |")
    out.append("|---|" + "---|" * len(LEVELS))
    for t in tools:
        c = s["tools"][t]["by_level"]
        out.append(f"| {t} | " + " | ".join(_fmt(c[lv]) for lv in LEVELS) + " |")

    out += ["", "## Paired discrimination by obfuscation level (Clopper-Pearson)", ""]
    out.append("| Tool | " + " | ".join(LEVELS) + " |")
    out.append("|---|" + "---|" * len(LEVELS))
    for t in tools:
        c = s["tools"][t]["paired_by_level"]
        out.append(f"| {t} | " + " | ".join(_fmt(c[lv]) for lv in LEVELS) + " |")

    out += ["", "## Recall by library", ""]
    out.append("| Tool | " + " | ".join(LIBS) + " |")
    out.append("|---|" + "---|" * len(LIBS))
    for t in tools:
        c = s["tools"][t]["by_lib"]
        out.append(f"| {t} | " + " | ".join(_fmt(c[lb]) for lb in LIBS) + " |")

    out += ["", "## Per-class heatmap: recall, leaky files flagged / leaky files", ""]
    out.append("Shading: blank 0, ░ < 25%, ▒ < 50%, ▓ < 75%, █ >= 75%. Last column: levels at "
               "which at least one linter flags at least one leaky file.")  # fmt: skip
    out.append("")
    out.append("| Class | " + " | ".join(linters) + " | caught at |")
    out.append("|---|" + "---|" * (len(linters) + 1))
    for cls in CLASSES:
        cells_ = []
        for t in linters:
            c = s["tools"][t]["by_class"][cls]
            cells_.append(f"{_shade(c['rate'])} {c['k']}/{c['n']}")
        lv = [lvl for lvl, ok in s["coverage"]["caught"][cls].items() if ok]
        out.append(f"| {cls} | " + " | ".join(cells_) + f" | {', '.join(lv) or 'none'} |")

    out += ["", "## False positives by class (clean twins flagged / clean twins)", ""]
    out.append("| Class | " + " | ".join(linters) + " |")
    out.append("|---|" + "---|" * len(linters))
    for cls in CLASSES:
        row = []
        for t in linters:
            c = s["tools"][t]["fpr_by_class"][cls]
            row.append(f"{c['k']}/{c['n']}" if c["k"] else "0")
        out.append(f"| {cls} | " + " | ".join(row) + " |")

    out += ["", "## Paired tool comparisons (exact McNemar, Holm over all rows)", ""]
    out.append("| A | B | Measure | only A | only B | p | p (Holm) |")
    out.append("|---|---|---|---|---|---|---|")
    for t in s["mcnemar"]:
        out.append(
            f"| {t['a']} | {t['b']} | {t['measure']} | {t['only_a']} | {t['only_b']} | "
            f"{t['p']:.3g} | {t['p_holm']:.3g} |"
        )
    out += ["", "## Coverage", ""]
    unc = s["coverage"]["uncaught_classes"]
    out.append("Classes no linter flags at any level: " + (", ".join(unc) if unc else "none") + ".")
    out += ["", "## False positives (clean twins flagged, file:line rule)", ""]
    for fp in s["false_positives"]:
        out.append(f"- {fp['tool']}: `{fp['file']}:{fp['line']}` {fp['rule']} ({fp['cls']}, "
                   f"{fp['level']}, {fp['lib']})")  # fmt: skip
    out += ["", "## Leaky L0 files no linter flags (file:site lines)", ""]
    for m in s["missed_l0"]:
        out.append(f"- `{m['file']}:{','.join(map(str, m['lines']))}` ({m['cls']}, {m['lib']})")
    return "\n".join(out) + "\n"


def write_report(corpus: Path, results: Path, *, n_boot: int = 10_000) -> dict:
    summary = build_summary(Path(corpus), Path(results), n_boot=n_boot)
    (Path(results) / "summary.json").write_text(
        json.dumps(summary, indent=1, sort_keys=True, default=float) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (Path(results) / "scorecard.md").write_text(
        render_markdown(summary), encoding="utf-8", newline="\n"
    )
    return summary
