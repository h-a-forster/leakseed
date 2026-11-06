"""Do the rules behind the corpus's zero-coverage classes fire on the forms they document?

The files in corpus/probes are hand-written leak/clean pairs in the surface forms those rules
look for. They are not part of corpus v1 and no rate is computed from them. The oracle checks
each label; every linter runs over the set. Writes results/v1/probes.md.
"""

from __future__ import annotations

from pathlib import Path

from leakseed.adapters import ADAPTERS, get
from leakseed.data import make_data
from leakseed.oracle import check, load_run

ROOT = Path(__file__).resolve().parents[1]
PROBES = ROOT / "corpus" / "probes"
OUT = ROOT / "results" / "v1" / "probes.md"


def main() -> None:
    data = make_data(1500, 2026)
    paths = sorted((PROBES / "files").glob("*.py"))
    for path in paths:
        label = path.stem.rsplit("_", 1)[1]
        verdict = check(load_run(path), data, seed=0)[0]
        if verdict != label:
            raise SystemExit(f"{path.name}: oracle says {verdict}")
    fired: dict[str, dict[str, set[str]]] = {p.name: {} for p in paths}
    for name in ADAPTERS:
        adapter = get(name)
        for f in adapter.run(PROBES)[0]:
            if adapter.counts(f):
                fired[Path(f.path).name].setdefault(name, set()).add(f.rule)
    lines = [
        "# Rule probes",
        "",
        "Hand-written pairs in the surface forms the rules look for (corpus/probes). The oracle "
        "confirms each label. Regenerate with `uv run python scripts/probes.py`.",
        "",
        "| File | Rules that fired |",
        "|---|---|",
    ]
    for name, by_tool in fired.items():
        hits = "; ".join(f"{t}: {', '.join(sorted(rules))}" for t, rules in by_tool.items())
        lines.append(f"| `{name}` | {hits or 'none'} |")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(OUT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
