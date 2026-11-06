# leakseed

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](pyproject.toml)

A seeded corpus of look-ahead leaks in backtest code. Each leaky script is paired with a
clean twin that differs only by the minimal fix, and every label is checked by a causality
oracle rather than taken from the template. The repository also scores the existing leakage
linters against the corpus, independently of their authors' own tests.

- **Corpus v1** ([corpus/v1](corpus/v1)): 368 scripts = 184 leak/clean pairs. They cover 15
  leak classes x 4 obfuscation levels (L0 direct call, L1 through a local name, L2 inside a
  helper, L3 config-driven) x pandas/numpy/polars, from 30 templates. The JSONL manifest gives
  each file's class, level, library, label and the line numbers of the leak (or fix).
- **Oracle** ([oracle.py](src/leakseed/oracle.py)): every script exposes
  `run(data) -> positions`. The oracle replaces all inputs after a time t (16 random cuts per
  mode; three modes: values, availability, trend regime; point-in-time records perturbed by
  filing time). Then it checks whether the positions held up to t + 1 move. All 368 labels
  are confirmed on the default data seed and on three more data seeds.
- **Scorecard**: adapters for lookahead-lint, peekproof, backtest-audit and leakguard, plus a
  null baseline (ruff defaults). Rates come with intervals from a cluster bootstrap over
  templates.

## Headline scorecard (corpus v1)

Each tool's documented leakage rules, 184 leaky files and 184 clean twins. 95% intervals
come from a cluster bootstrap over the 30 templates (10,000 resamples). Paired
discrimination = flags the leaky file and not its twin. Localisation = a flag within ±2
lines of the seeded site, among flagged leaky files.

| Tool | Version | Recall | False-positive rate | Paired discrimination | Localisation |
|---|---|---|---|---|---|
| peekproof | git e6c56c3 | 21.2% [10.6, 32.7] (39/184) | 3.8% [1.1, 6.9] (7/184) | 17.4% [9.1, 26.1] (32/184) | 39/39 |
| leakguard (static core) | 0.1.1 | 17.4% [8.5, 27.7] (32/184) | 6.0% [1.3, 12.2] (11/184) | 11.4% [5.5, 18.2] (21/184) | 32/32 |
| lookahead-lint | 1.0.1 | 7.6% [2.3, 14.7] (14/184) | 2.2% [0.0, 6.2] (4/184) | 5.4% [1.8, 9.8] (10/184) | 14/14 |
| backtest-audit | 1.0.0 | 4.3% [0.0, 11.1] (8/184) | 2.2% [0.0, 7.3] (4/184) | 2.2% [0.0, 7.0] (4/184) | 8/8 |
| ruff defaults (null) | 0.17.1 | 0.0% (0/184) | 0.0% (0/184) | 0.0% (0/184) | - |
| any of the four | - | 34.2% [21.5, 47.4] (63/184) | 11.4% [4.6, 19.4] (21/184) | 22.8% [13.8, 32.1] (42/184) | - |

What stands out:

- **Obfuscation.** Recall falls from the direct call to any indirection: peekproof catches
  20/46 at L0 and 6 or 7 at L1-L3. At L3 (config-driven) no tool flags a leaky file
  without also flagging its clean twin (paired discrimination 0/46 for every tool).
- **Coverage.** No linter flags any leaky file, at any level, in 6 of the 15 classes:
  same-bar execution, restated fundamentals, survivorship, `np.roll` wraparound, reversed
  cumulative statistics and a parameter tuned on the full sample.
- **Ties at the top.** peekproof and leakguard do not differ significantly (exact McNemar,
  Holm-adjusted p = 0.48 on recall and 0.28 on paired discrimination). Both beat
  lookahead-lint and backtest-audit.

Full results, the per-class heatmap and every false positive with file:line:
[REPORT.md](REPORT.md) and [results/v1/scorecard.md](results/v1/scorecard.md).

## What the corpus is and is not

- It covers **code-level look-ahead**: a script's output at time t depends on data after t.
  It does not cover LLM-knowledge leakage (a model that remembers the future); that is what
  Look-Ahead-Bench measures. It also leaves out ML train/test leakage that has no time
  dimension.
- The scripts are **synthetic and small** (6 to 37 lines). Templates are written in a
  neutral style without vendor APIs (no yfinance) or suggestive names (no `constituents`).
  Rules keyed to those surface forms score zero here by design; [REPORT.md](REPORT.md) lists
  them.
- A **leak label is a proof**: the oracle produces a concrete witness (cut t, perturbation,
  row). A **clean label is evidence**: no tried perturbation moved the past. See
  [docs/DESIGN.md](docs/DESIGN.md) for the soundness argument and its limits.
- **v1 is frozen.** Tools may be tuned on a public corpus. Later versions add a fresh
  generator seed (new surface forms of the same design) and report both.

## Quick start

```sh
uv sync                                  # project + pinned linters (dev group)
uv run leakseed generate --check         # v1 matches its manifest and regenerates byte for byte
uv run leakseed verify --workers 3       # oracle on all 368 files (about 90 s)
uv run leakseed score --tool all         # run the five tools, store findings
uv run leakseed report                   # results/v1/summary.json + scorecard.md
uv run leakseed generate --seed 7 --out tmp/c7   # a fresh corpus from another seed
```

The oracle runs only corpus files whose SHA-256 matches the manifest. The linters run
statically (no tool executes corpus code). No network or model calls at run time.

## Layout

| Path | What |
|---|---|
| `src/leakseed/templates/` | rendering framework (`core.py`) and the 15 leak classes (`classes.py`) |
| `src/leakseed/data.py` | synthetic market data and the after-t perturbations |
| `src/leakseed/oracle.py` | causality oracle and `verify` |
| `src/leakseed/adapters/` | one adapter per linter, output -> (file, line, rule) |
| `src/leakseed/score.py`, `stats.py`, `report.py` | estimands, intervals, McNemar, scorecard |
| `corpus/v1/` | frozen corpus: `files/`, `manifest.jsonl`, `VERSION.json` |
| `results/v1/` | oracle verdicts, tool findings, `summary.json`, `scorecard.md` |
| `docs/DESIGN.md` | taxonomy, oracle soundness, statistics, threat model, tool vetting |
| `docs/upstream/` | draft issues for the linters (not filed) |

## Citing

See [CITATION.cff](CITATION.cff). MIT licence.
