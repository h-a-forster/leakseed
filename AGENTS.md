# AGENTS.md

Guide for coding agents (and humans) working on leakseed. Read `docs/DESIGN.md` before
changing the oracle, the estimands or a template: it holds the taxonomy, the oracle contract,
the statistics, the threat model and the tool vetting this file points to.

## What this is

A frozen corpus of look-ahead leaks in small backtest scripts, in leak/clean twin pairs whose
labels are checked by executing each script, and a scorecard of static leakage linters on it.
Static tools only; the corpus covers code-level look-ahead, not what an LLM remembers.

## Conventions

- uv + hatchling, `src/` layout, Python >= 3.12 (`.python-version` 3.12), `ruff check` +
  `ruff format` (line length 100), pytest. `[tool.uv] exclude-newer` keeps the lock on
  releases at least two weeks old; move it deliberately.
- **v1 is frozen.** Do not change `corpus/v1`, `V1_SEED`, or anything that alters what the
  generator renders for it: `leakseed generate --check` must keep passing. Template changes
  go into a new version under a new seed.
- The oracle decides labels. If a template and the oracle disagree, fix the template or show
  the oracle is wrong with a test; never relax it to fit.
- `verify`, `impact` and `probes.py` execute Python. They run only our generated files
  (hash-checked against the manifest) and the fixed probes. Linters run statically.
- A new tool is read as text before it is installed or run (DESIGN.md, section 6) and pinned
  in the `tools` group. Tool failures raise; they never count as "no finding".
- Results under `results/` are generated; never edit them. README and REPORT tables are copies
  of rows in `results/v1/published.md`, and the README's headline prose between the generated
  markers is rendered by `leakseed report --readme README.md`; change `published.py`, not the
  copies. `tests/test_published.py` and CI hold them to the committed results. `oracle.jsonl`, `findings/` and
  `impact.jsonl` are reproducible byte for byte on one platform. Each results directory has a
  `corpus.json` with its corpus's manifest hash, and the commands refuse to mix two corpora
  there, so scratch corpora need their own `--out`.
- No model or network calls at run time.

## Architecture map

| Path | Role |
|---|---|
| `src/leakseed/templates/` | `core.py` renders a program and marks its site; `classes.py` holds the 15 leak classes |
| `src/leakseed/generate.py` | corpus writing, manifest, hash checks, the frozen-snapshot check |
| `src/leakseed/data.py` | synthetic market data and the after-t perturbations |
| `src/leakseed/oracle.py` | causality oracle and `verify` |
| `src/leakseed/impact.py` | Sharpe of each file on drift-free data |
| `src/leakseed/adapters/` | one adapter per linter, tool output to `Finding` |
| `src/leakseed/score.py`, `stats.py` | estimands; bootstrap, Clopper-Pearson, McNemar, template sign-flip, Holm |
| `src/leakseed/report.py` | `summary.json` and `scorecard.md` |
| `src/leakseed/published.py` | `published.md`: the README and REPORT tables and the README's headline prose |
| `src/leakseed/cli.py` | `generate / verify / impact / score / report` |
| `scripts/probes.py` | runs the linters over `corpus/probes`, writes `results/v1/probes.md` |
| `corpus/v1/` | frozen corpus |
| `corpus/probes/` | hand-written pairs for rules the v1 style cannot trigger; no rates from these |
| `results/v1/` | oracle verdicts, findings, impact, summary, scorecard, probes, corpus stamp |
| `results/fresh/` | scorecards of two fresh generator seeds (their corpora regenerate from the seed) |
| `docs/upstream.md` | issues filed with the linters and their state; drafts in `docs/upstream/` |

## How to test

```sh
uv sync
uv run pytest                         # under a minute, offline
uv run ruff check .
uv run ruff format --check .
uv lock --check
uv run leakseed generate --check
```

Full study (about 5 minutes with 3 workers): `leakseed verify --workers 3`,
`leakseed impact`, `leakseed score --tool all`, `leakseed report --readme README.md`,
`uv run python scripts/probes.py`. `git diff results/` should then be empty.

## Status

Open work is in `backlog.md` (gitignored, local only). The repository is public; v0.1.0 is tagged
and released.
