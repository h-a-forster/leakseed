"""Command line: generate, verify, score, report."""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from collections import Counter
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .adapters import ADAPTERS, get
from .adapters.base import executable, findings_to_jsonl, run_tool
from .data import PERTURB_MODES
from .generate import V1_SEED, VERSION_FILE, CorpusError, check_snapshot, read_manifest, write
from .impact import DATA_SEEDS, measure, write_impact
from .oracle import DATA_SEED, verify, write_verdicts
from .report import write_report

DEFAULT_CORPUS = Path("corpus/v1")
DEFAULT_RESULTS = Path("results/v1")
RESULTS_STAMP = "corpus.json"  # which corpus a results directory belongs to


def _check_results(corpus: Path, results: Path) -> str:
    """Return the corpus manifest hash, refusing ``results`` if they belong to another corpus."""
    version = json.loads((corpus / VERSION_FILE).read_text(encoding="utf-8"))
    sha = version["manifest_sha256"]
    stamp = results / RESULTS_STAMP
    if stamp.is_file() and json.loads(stamp.read_text("utf-8"))["manifest_sha256"] != sha:
        raise CorpusError(f"{results} holds results of another corpus than {corpus}; pass --out")
    return sha


def _claim_results(corpus: Path, results: Path) -> None:
    """Tie ``results`` to ``corpus``. Every command that writes results calls this first."""
    sha = _check_results(corpus, results)
    results.mkdir(parents=True, exist_ok=True)
    (results / RESULTS_STAMP).write_text(
        json.dumps({"manifest_sha256": sha}, indent=1) + "\n", "utf-8", newline="\n"
    )


def _generate(args: argparse.Namespace) -> int:
    if args.check:
        version = check_snapshot(args.out)
        print(f"{args.out}: {version['files']} files match seed {version['seed']}")
        return 0
    rows = write(args.out, args.seed)
    print(f"wrote {len(rows)} files to {args.out} (seed {args.seed})")
    return 0


def _verify(args: argparse.Namespace) -> int:
    ids = None
    if args.sample:
        manifest = read_manifest(args.corpus)
        pairs = sorted({tuple(sorted((r["id"], r["twin"]))) for r in manifest})
        chosen = random.Random(args.sample_seed).sample(pairs, min(args.sample, len(pairs)))
        ids = [i for pair in chosen for i in pair]
    if args.out and not ids:
        _claim_results(args.corpus, args.out)
    start = time.perf_counter()
    done = Counter()

    def progress(v):
        done[v.verdict == v.label] += 1
        if args.verbose or v.verdict != v.label:
            print(f"{v.id} label={v.label} verdict={v.verdict} {v.error or v.witness or ''}")

    verdicts = verify(args.corpus, n=args.n, n_t=args.n_t, workers=args.workers,
                      data_seed=args.data_seed, ids=ids, progress=progress)  # fmt: skip
    bad = [v for v in verdicts if v.verdict != v.label]
    seconds = time.perf_counter() - start
    print(f"{len(verdicts) - len(bad)}/{len(verdicts)} labels confirmed in {seconds:.0f}s")
    if args.out and not ids and args.data_seed == DATA_SEED:
        write_verdicts(args.out / "oracle.jsonl", verdicts)
        meta = {"n": args.n, "n_t": args.n_t, "data_seed": DATA_SEED, "modes": list(PERTURB_MODES)}
        (args.out / "oracle_meta.json").write_text(
            json.dumps(meta, indent=1) + "\n", "utf-8", newline="\n"
        )
    elif args.out and not ids:
        path = args.out / "oracle_replication.json"
        done_seeds = json.loads(path.read_text("utf-8")) if path.is_file() else {}
        done_seeds[str(args.data_seed)] = {
            "agree": len(verdicts) - len(bad),
            "total": len(verdicts),
        }
        path.write_text(
            json.dumps(done_seeds, indent=1, sort_keys=True) + "\n", "utf-8", newline="\n"
        )
    return 1 if bad else 0


def _impact(args: argparse.Namespace) -> int:
    _claim_results(args.corpus, args.out)
    rows = measure(args.corpus, n=args.n, data_seeds=tuple(args.data_seeds))
    write_impact(args.out / "impact.jsonl", rows)
    print(
        f"wrote {args.out / 'impact.jsonl'} ({len(rows)} files, {len(args.data_seeds)} data seeds)"
    )
    return 0


def _tool_version(name: str) -> str:
    if name == "ruff-defaults":
        return run_tool([executable("ruff"), "--version"], Path("."), (0,)).split()[-1]
    return get(name).version


def _score(args: argparse.Namespace) -> int:
    names = list(ADAPTERS) if args.tool == "all" else [args.tool]
    out = args.out
    _claim_results(args.corpus, out)
    (out / "findings").mkdir(parents=True, exist_ok=True)
    meta_path = out / "tools.json"
    meta = json.loads(meta_path.read_text("utf-8")) if meta_path.is_file() else {}
    manifest = read_manifest(args.corpus)
    labels = {r["path"]: r["label"] for r in manifest}
    for name in names:
        adapter = get(name)
        start = time.perf_counter()
        findings, _raw = adapter.run(args.corpus)
        (out / "findings" / f"{name}.jsonl").write_text(
            findings_to_jsonl(findings), encoding="utf-8", newline="\n"
        )
        meta[name] = {"package": adapter.package, "version": _tool_version(name)}
        flagged = {f.path for f in findings if adapter.counts(f)}
        leak = sum(labels[p] == "leak" for p in flagged)
        clean = len(flagged) - leak
        print(f"{name}: {len(findings)} findings; flags {leak} leaky and {clean} clean files "
              f"({time.perf_counter() - start:.1f}s)")  # fmt: skip
    meta_path.write_text(json.dumps(meta, indent=1, sort_keys=True) + "\n", "utf-8", newline="\n")
    return 0


def _report(args: argparse.Namespace) -> int:
    _check_results(args.corpus, args.results)
    summary = write_report(args.corpus, args.results, n_boot=args.bootstrap)
    for name, t in summary["tools"].items():
        p = t["primary"]
        print(f"{name:15s} recall {p['recall']['rate']:.3f}  fpr {p['fpr']['rate']:.3f}  "
              f"paired {p['paired']['rate']:.3f}")  # fmt: skip
    print(f"wrote {args.results / 'summary.json'} and {args.results / 'scorecard.md'}")
    if summary["oracle"]["disagree"]:
        print(f"oracle disagrees with {len(summary['oracle']['disagree'])} labels", file=sys.stderr)
        return 1
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="leakseed", description=__doc__)
    parser.add_argument("--version", action="version", version=f"leakseed {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    g = sub.add_parser("generate", help="write a corpus from a seed, or check a frozen one")
    g.add_argument("--seed", type=int, default=V1_SEED)
    g.add_argument("--out", type=Path, default=DEFAULT_CORPUS)
    g.add_argument("--check", action="store_true", help="check --out against its manifest and seed")
    g.set_defaults(func=_generate)

    v = sub.add_parser("verify", help="run the causality oracle on every corpus file")
    v.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    v.add_argument("--out", type=Path, default=DEFAULT_RESULTS)
    v.add_argument("--n", type=int, default=5000, help="rows of synthetic data")
    v.add_argument("--n-t", type=int, default=16, help="cut points per perturbation mode")
    v.add_argument("--workers", type=int, default=1)
    v.add_argument("--data-seed", type=int, default=DATA_SEED,
                   help="synthetic data seed; only the default writes results")  # fmt: skip
    v.add_argument("--sample", type=int, default=0, help="verify only this many random pairs")
    v.add_argument("--sample-seed", type=int, default=0)
    v.add_argument("--verbose", action="store_true")
    v.set_defaults(func=_verify)

    i = sub.add_parser("impact", help="measure each file's Sharpe ratio on driftless data")
    i.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    i.add_argument("--out", type=Path, default=DEFAULT_RESULTS)
    i.add_argument("--n", type=int, default=5000, help="rows of synthetic data")
    i.add_argument("--data-seeds", type=int, nargs="+", default=list(DATA_SEEDS))
    i.set_defaults(func=_impact)

    s = sub.add_parser("score", help="run a linter over the corpus and store its findings")
    s.add_argument("--tool", required=True, choices=[*ADAPTERS, "all"])
    s.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    s.add_argument("--out", type=Path, default=DEFAULT_RESULTS)
    s.set_defaults(func=_score)

    r = sub.add_parser("report", help="write summary.json and scorecard.md")
    r.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    r.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    r.add_argument("--bootstrap", type=int, default=10_000)
    r.set_defaults(func=_report)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
