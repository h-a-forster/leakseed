"""Scorecard: combine the manifest, oracle verdicts and every tool's findings."""

from __future__ import annotations

import itertools
import json
from collections import Counter
from pathlib import Path
from statistics import median

from .adapters import ADAPTERS, get
from .generate import VERSION_FILE, read_manifest, read_source
from .score import cells, estimands, file_outcomes, read_findings, site_hit, window_share
from .stats import clopper_pearson, cluster_sign_test, holm, mcnemar_exact
from .templates import CLASSES, LEVELS, LIBS

BASELINE = "ruff-defaults"
# A leaky file is material when its annualised |Sharpe| on drift-free data reaches this.
MATERIAL = 1.0


def _fmt(e: dict) -> str:
    if e["n"] == 0:
        return "n/a (0 files)"
    return f"{100 * e['rate']:.1f}% [{100 * e['lo']:.1f}, {100 * e['hi']:.1f}] ({e['k']}/{e['n']})"


def _pct(e: dict) -> str:
    return "n/a" if e["n"] == 0 else f"{e['k']}/{e['n']}"


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
    window = {}
    for r in manifest:
        lines = read_source(corpus, r).splitlines()
        window[r["id"]] = window_share(
            r["site_lines"], [i for i, text in enumerate(lines, 1) if text.strip()]
        )

    tools_meta = json.loads((results / "tools.json").read_text(encoding="utf-8"))
    tools: dict[str, dict] = {}
    outcomes_by_tool: dict[str, dict] = {}
    for name in ADAPTERS:
        adapter = get(name)
        findings = read_findings(results / "findings" / f"{name}.jsonl")
        primary = file_outcomes(manifest, findings, adapter)
        anyrule = file_outcomes(manifest, findings, adapter, any_rule=True)
        strict = file_outcomes(manifest, findings, adapter, strict=True)
        outcomes_by_tool[name] = primary
        tools[name] = {
            "version": tools_meta[name]["version"],
            "leak_rules": sorted(adapter.leak_rules) if adapter.leak_rules else "all",
            "findings": len(findings),
            "rules_seen": dict(Counter(f.rule for f in findings).most_common()),
            "top_severity": adapter.top_severity,
            "primary": estimands(manifest, primary, n_boot=n_boot, seed=seed, window=window),
            "any_rule": estimands(manifest, anyrule, n_boot=n_boot, seed=seed),
            "strict": estimands(manifest, strict, n_boot=n_boot, seed=seed),
            "by_level": _cells(manifest, primary, ("level",)),
            "fpr_by_level": _cells(manifest, primary, ("level",), label="clean"),
            "paired_by_level": _paired_cells(leak_rows, primary, "level"),
            "paired_site_by_level": _paired_cells(leak_rows, primary, "level", at_site=True),
            "paired_site_by_class": _paired_cells(leak_rows, primary, "cls", at_site=True),
            "by_lib": _cells(manifest, primary, ("lib",)),
            "by_class": _cells(manifest, primary, ("cls",)),
            "fpr_by_class": _cells(manifest, primary, ("cls",), label="clean"),
            "by_class_level": _cells(manifest, primary, ("cls", "level")),
        }

    linters = [n for n in ADAPTERS if n != BASELINE]
    tests = []
    groups = [r["template"] for r in leak_rows]
    for a, b in itertools.combinations(linters, 2):
        oa, ob = outcomes_by_tool[a], outcomes_by_tool[b]
        rec_a = [oa[r["id"]]["flagged"] for r in leak_rows]
        rec_b = [ob[r["id"]]["flagged"] for r in leak_rows]
        site_a = [site_hit(oa, r) for r in leak_rows]
        site_b = [site_hit(ob, r) for r in leak_rows]
        for measure, x, y in (("recall", rec_a, rec_b), ("paired at the site", site_a, site_b)):
            tests.append({"a": a, "b": b, "measure": measure, **mcnemar_exact(x, y),
                          "p_cluster": cluster_sign_test(x, y, groups)})  # fmt: skip
    for measure in ("recall", "paired at the site"):
        family = [t for t in tests if t["measure"] == measure]
        for t, p in zip(family, holm([t["p_cluster"] for t in family]), strict=True):
            t["p_cluster_holm"] = p

    caught = {
        cls: {
            lvl: any(
                site_hit(outcomes_by_tool[t], r)
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
    union_site = {
        r["id"]: any(site_hit(outcomes_by_tool[t], r) for t in linters) for r in leak_rows
    }
    union_outcomes = {
        r["id"]: {
            "flagged": union[r["id"]],
            "localised": False,
            "exact": union_site.get(r["id"], False),  # at least one tool, on its own
            "either": False,
        }
        for r in manifest
    }
    union_est = estimands(manifest, union_outcomes, n_boot=n_boot)

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
        if r["level"] == "L0" and not union_site[r["id"]]
    ]
    impact_path = results / "impact.jsonl"
    if not impact_path.is_file():
        raise FileNotFoundError(f"no {impact_path}; run `leakseed impact` first")
    sharpes = {
        row["id"]: row["sharpe"]
        for row in map(json.loads, impact_path.read_text(encoding="utf-8").splitlines())
    }
    if set(sharpes) != {r["id"] for r in manifest}:
        raise ValueError("impact rows do not cover exactly the manifest files")
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
        "impact": _impact_table(leak_rows, sharpes, outcomes_by_tool, linters, union_site),
        "mcnemar": tests,
        "coverage": {
            "caught": caught,
            "uncaught_classes": [c for c, lv in caught.items() if not any(lv.values())],
        },
        "false_positives": fps,
        "missed_l0": missed_l0,
    }


def _impact_table(leak_rows, sharpes, outcomes_by_tool, linters, union_site):
    """|Sharpe| of leaky files and their twins, and which material leaks are found at the site."""
    classes = {}
    for cls in CLASSES:
        rows = [r for r in leak_rows if r["cls"] == cls]
        material = [r for r in rows if abs(sharpes[r["id"]]) >= MATERIAL]
        classes[cls] = {
            "pairs": len(rows),
            "median_abs_leaky": round(median(abs(sharpes[r["id"]]) for r in rows), 3),
            "max_abs_leaky": round(max(abs(sharpes[r["id"]]) for r in rows), 3),
            "median_abs_clean": round(median(abs(sharpes[r["twin"]]) for r in rows), 3),
            "material": len(material),
            "material_found": sum(union_site[r["id"]] for r in material),
        }
    material = [r for r in leak_rows if abs(sharpes[r["id"]]) >= MATERIAL]
    return {
        "threshold": MATERIAL,
        "max_abs_clean": max(abs(sharpes[r["twin"]]) for r in leak_rows),
        "classes": classes,
        "material_pairs": len(material),
        "material_found_by_tool": {
            t: sum(site_hit(outcomes_by_tool[t], r) for r in material) for t in linters
        },
        "material_found_by_any": sum(union_site[r["id"]] for r in material),
    }


def _paired_cells(leak_rows, outcomes, key, *, at_site=False):
    """Paired discrimination per value of ``key``, with Clopper-Pearson."""
    out = {}
    for value in sorted({r[key] for r in leak_rows}):
        rows = [r for r in leak_rows if r[key] == value]
        k = sum(
            site_hit(outcomes, r)
            if at_site
            else outcomes[r["id"]]["flagged"] and not outcomes[r["twin"]]["flagged"]
            for r in rows
        )
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
        "| Tool | Version | Recall | False-positive rate | Paired discrimination | "
        "Paired at the site |"
    )
    out.append("|---|---|---|---|---|---|")
    for t in tools:
        p = s["tools"][t]["primary"]
        out.append(
            f"| {t} | {s['tools'][t]['version']} | {_fmt(p['recall'])} | {_fmt(p['fpr'])} | "
            f"{_fmt(p['paired'])} | {_fmt(p['paired_site'])} |"
        )
    u = s["union"]
    out.append(
        f"| any linter | - | {_fmt(u['recall'])} | {_fmt(u['fpr'])} | "
        f"{_fmt(u['paired'])} | {_fmt(u['paired_site'])} |"
    )
    out += ["", "## Balanced over classes", ""]
    out.append("Pooled rates weight classes by their file counts. These are means of class rates.")
    out.append("")
    out.append("| Tool | Recall | Paired at the site |")
    out.append("|---|---|---|")
    for t in linters:
        p = s["tools"][t]["primary"]
        out.append(
            f"| {t} | {100 * p['recall_class_mean']:.1f}% | "
            f"{100 * p['paired_site_class_mean']:.1f}% |"
        )
    out += ["", "## Localisation (leaky files flagged)", ""]
    out.append(
        "Within 2 lines of a site line, on a site line, and what a random code line of the same "
        "files would score within 2 lines."
    )
    out.append("")
    out.append("| Tool | Within 2 lines | On a site line | Random line within 2 |")
    out.append("|---|---|---|---|")
    for t in linters:
        p = s["tools"][t]["primary"]
        chance = p.get("localisation_chance")
        shown = "n/a" if chance is None else f"{100 * chance:.0f}%"
        out.append(
            f"| {t} | {_pct(p['localisation'])} | {_pct(p['localisation_exact'])} | {shown} |"
        )
    out += ["", "## Sensitivity: the tool's top severity only", ""]
    out.append("Tools without grades are unchanged (peekproof high, leakguard error, "
               "overfit-gauntlet error, monte-neo fail).")  # fmt: skip
    out.append("")
    out.append("| Tool | Recall | False-positive rate | Paired at the site |")
    out.append("|---|---|---|---|")
    for t in linters:
        if s["tools"][t]["top_severity"]:
            p = s["tools"][t]["strict"]
            out.append(
                f"| {t} | {_fmt(p['recall'])} | {_fmt(p['fpr'])} | {_fmt(p['paired_site'])} |"
            )
    out += ["", "## Sensitivity: every rule counts", ""]
    out.append("| Tool | Recall | False-positive rate | Paired at the site |")
    out.append("|---|---|---|---|")
    for t in tools:
        p = s["tools"][t]["any_rule"]
        out.append(f"| {t} | {_fmt(p['recall'])} | {_fmt(p['fpr'])} | {_fmt(p['paired_site'])} |")

    out += ["", "## Recall by obfuscation level (Clopper-Pearson)", ""]
    out.append("| Tool | " + " | ".join(LEVELS) + " |")
    out.append("|---|" + "---|" * len(LEVELS))
    for t in tools:
        c = s["tools"][t]["by_level"]
        out.append(f"| {t} | " + " | ".join(_fmt(c[lv]) for lv in LEVELS) + " |")

    out += ["", "## False-positive rate by obfuscation level (Clopper-Pearson)", ""]
    out.append("Both L3 twins contain the leaky expression in a branch the config turns off.")
    out.append("")
    out.append("| Tool | " + " | ".join(LEVELS) + " |")
    out.append("|---|" + "---|" * len(LEVELS))
    for t in tools:
        c = s["tools"][t]["fpr_by_level"]
        out.append(f"| {t} | " + " | ".join(_fmt(c[lv]) for lv in LEVELS) + " |")

    for key, title in (("paired_by_level", "Paired discrimination"),
                       ("paired_site_by_level", "Paired at the site")):  # fmt: skip
        out += ["", f"## {title} by obfuscation level (Clopper-Pearson)", ""]
        out.append("| Tool | " + " | ".join(LEVELS) + " |")
        out.append("|---|" + "---|" * len(LEVELS))
        for t in tools:
            c = s["tools"][t][key]
            out.append(f"| {t} | " + " | ".join(_fmt(c[lv]) for lv in LEVELS) + " |")

    out += ["", "## Recall by library", ""]
    out.append("| Tool | " + " | ".join(LIBS) + " |")
    out.append("|---|" + "---|" * len(LIBS))
    for t in tools:
        c = s["tools"][t]["by_lib"]
        out.append(f"| {t} | " + " | ".join(_fmt(c[lb]) for lb in LIBS) + " |")

    out += ["", "## Per-class heatmap: recall, leaky files flagged / leaky files", ""]
    out.append("Shading: blank 0, ░ < 25%, ▒ < 50%, ▓ < 75%, █ >= 75%.")
    out.append("")
    out.append("| Class | " + " | ".join(linters) + " |")
    out.append("|---|" + "---|" * len(linters))
    for cls in CLASSES:
        row = []
        for t in linters:
            c = s["tools"][t]["by_class"][cls]
            row.append(f"{_shade(c['rate'])} {c['k']}/{c['n']}")
        out.append(f"| {cls} | " + " | ".join(row) + " |")

    out += ["", "## Per-class heatmap: paired at the site", ""]
    out.append("Pairs with a flag on a site line of the leaky file and none at the same place in "
               "its twin. Last column: levels where at least one linter does this.")  # fmt: skip
    out.append("")
    out.append("| Class | " + " | ".join(linters) + " | found at |")
    out.append("|---|" + "---|" * (len(linters) + 1))
    for cls in CLASSES:
        row = []
        for t in linters:
            c = s["tools"][t]["paired_site_by_class"][cls]
            row.append(f"{_shade(c['rate'])} {c['k']}/{c['n']}")
        lv = [lvl for lvl, ok in s["coverage"]["caught"][cls].items() if ok]
        out.append(f"| {cls} | " + " | ".join(row) + f" | {', '.join(lv) or 'none'} |")

    imp = s["impact"]
    out += ["", "## Size of the leak: |Sharpe| on drift-free data, by class", ""]
    out.append(
        "Annualised, mean over the data seeds; the sign only says which way the template trades. "
        f"Material: |Sharpe| of the leaky file >= {imp['threshold']:g} (largest clean twin: "
        f"{imp['max_abs_clean']:.2f}). Found: paired at the site by at least one linter. "
        "Events and fundamentals are independent of prices in this data, so those classes "
        "cannot show a gain here."
    )
    out.append("")
    out.append("| Class | Median leaky | Largest leaky | Median clean | Material | Found |")
    out.append("|---|---|---|---|---|---|")
    for cls, row in imp["classes"].items():
        out.append(
            f"| {cls} | {row['median_abs_leaky']:.2f} | {row['max_abs_leaky']:.2f} | "
            f"{row['median_abs_clean']:.2f} | {row['material']}/{row['pairs']} | "
            f"{row['material_found']}/{row['material']} |"
        )
    out += ["", f"Material leaks found at the site, of {imp['material_pairs']}:", ""]
    for t, k in imp["material_found_by_tool"].items():
        out.append(f"- {t}: {k}")
    out.append(f"- any linter: {imp['material_found_by_any']}")

    out += ["", "## False positives by class (clean twins flagged / clean twins)", ""]
    out.append("| Class | " + " | ".join(linters) + " |")
    out.append("|---|" + "---|" * len(linters))
    for cls in CLASSES:
        row = []
        for t in linters:
            c = s["tools"][t]["fpr_by_class"][cls]
            row.append(f"{c['k']}/{c['n']}" if c["k"] else "0")
        out.append(f"| {cls} | " + " | ".join(row) + " |")

    out += ["", "## Paired tool comparisons", ""]
    out.append(
        "Exact McNemar treats files as independent. The template sign-flip test counts each "
        "template once and is the one to read; Holm runs within each measure."
    )
    out.append("")
    out.append("| A | B | Measure | only A | only B | McNemar p | Template p | Template p (Holm) |")
    out.append("|---|---|---|---|---|---|---|---|")
    for t in s["mcnemar"]:
        out.append(
            f"| {t['a']} | {t['b']} | {t['measure']} | {t['only_a']} | {t['only_b']} | "
            f"{t['p']:.3g} | {t['p_cluster']:.3g} | {t['p_cluster_holm']:.3g} |"
        )
    out += ["", "## Coverage", ""]
    unc = s["coverage"]["uncaught_classes"]
    out.append("Classes no linter finds at the site at any level: "
               + (", ".join(unc) if unc else "none") + ".")  # fmt: skip
    out += ["", "## False positives (clean twins flagged, file:line rule)", ""]
    for fp in s["false_positives"]:
        out.append(f"- {fp['tool']}: `{fp['file']}:{fp['line']}` {fp['rule']} ({fp['cls']}, "
                   f"{fp['level']}, {fp['lib']})")  # fmt: skip
    out += ["", "## Leaky L0 files no linter finds at the site (file:site lines)", ""]
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
