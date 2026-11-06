# leakseed

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](pyproject.toml)

A seeded corpus of look-ahead leaks in backtest code. Each leaky script is paired with a
clean twin that differs only by the minimal fix, and every label is checked by a causality
oracle rather than taken from the template. The repository also scores seven static leakage
linters on the corpus, independently of their authors' own tests.

- **Corpus v1** ([corpus/v1](corpus/v1)): 368 scripts = 184 leak/clean pairs. They cover 15
  leak classes x 4 obfuscation levels (L0 direct call, L1 through a local name, L2 inside a
  helper, L3 config-driven) x pandas/numpy/polars, from 30 templates. The JSONL manifest gives
  each file's class, level, library, label and the line numbers of the leak (or fix).
- **Oracle** ([oracle.py](src/leakseed/oracle.py)): every script exposes
  `run(data) -> positions`. The oracle replaces all inputs after a time t (16 cuts per mode;
  three modes: values, availability, trend regime; point-in-time records perturbed by filing
  time). Then it checks whether the positions held up to t + 1 move. All 368 labels are
  confirmed on four data seeds, and on two fresh generator seeds.
- **Scorecard**: adapters for seven linters and a null baseline (ruff defaults). Rates come
  with intervals from a cluster bootstrap over templates, and tool comparisons from an exact
  sign-flip test over templates.

## Headline scorecard (corpus v1)

Each tool's documented leakage rules at any severity, 184 leaky files and 184 clean twins. 95%
intervals come from a cluster bootstrap over the 30 templates (10,000 resamples). *Paired at
the site* means a flag on the leak and none at the same place in the clean twin, so a rule
that fires on code the twins share scores nothing. It is the measure to read.

| Tool | Version | Paired at the site | Recall | False-positive rate |
|---|---|---|---|---|
| monte-neo (lint only) | 0.54.0 | 33.2% [22.9, 43.4] (61/184) | 57.6% [44.6, 71.1] (106/184) | 31.5% [19.1, 46.4] (58/184) |
| peekproof | git e6c56c3 | 17.4% [9.1, 26.1] (32/184) | 21.2% [10.6, 32.7] (39/184) | 3.8% [1.1, 6.9] (7/184) |
| nofuturedata | git fb46880 | 12.0% [6.1, 19.2] (22/184) | 14.1% [6.7, 23.8] (26/184) | 2.2% [0.5, 4.5] (4/184) |
| leakguard (static core) | 0.1.1 | 11.4% [5.5, 18.2] (21/184) | 17.4% [8.5, 27.7] (32/184) | 6.0% [1.3, 12.2] (11/184) |
| overfit-gauntlet (lint) | 0.1.0 | 6.5% [2.1, 12.0] (12/184) | 11.4% [4.1, 19.9] (21/184) | 4.9% [0.5, 10.6] (9/184) |
| lookahead-lint | 1.0.1 | 5.4% [1.8, 9.8] (10/184) | 7.6% [2.3, 14.7] (14/184) | 2.2% [0.0, 6.2] (4/184) |
| backtest-audit | 1.0.0 | 2.2% [0.0, 7.0] (4/184) | 4.3% [0.0, 11.1] (8/184) | 2.2% [0.0, 7.3] (4/184) |
| ruff defaults (null) | 0.17.1 | 0.0% (0/184) | 0.0% (0/184) | 0.0% (0/184) |
| any linter | - | 39.7% [28.6, 50.5] (73/184) | 65.8% [51.5, 79.8] (121/184) | 36.4% [23.3, 51.6] (67/184) |

What stands out:

- **Noise.** monte-neo leads every other tool at the site (Holm-adjusted template p from
  0.0003 to 0.032), but much of its recall is warnings on code both twins share. At its `fail`
  severity alone its rates are 23.4% at the site and 4.3% false positives.
- **Size.** 61 leaky files reach |Sharpe| >= 1 on drift-free data; the largest clean twin
  reaches 0.20. No tool finds 43 of the 61 at the site.
- **Coverage.** No tool finds `same_bar`, `np_roll` or `argmax_param` at the site. These are
  gaps in form: PP010 fires once a `signal * returns` line exists, three tools catch a negative
  `np.roll`, and four catch a time-blind `GridSearchCV`
  ([results/v1/probes.md](results/v1/probes.md)).
- **Indirection.** Four of the seven tools lose more than half their score from L0 to L1, when
  a value passes through one local variable. monte-neo inlines constants and stays at 24/46.
  At L3 no tool separates the twins (0/46 each).
- **Comparisons.** 16 of the 21 tool pairs pass p < 0.05 with McNemar over files. Files of one
  template are correlated; 8 of 21 survive a sign-flip test over templates with Holm.

Per-class heatmaps, per-level tables, sensitivity analyses and every false positive with
file:line: [results/v1/scorecard.md](results/v1/scorecard.md).

## What the corpus is and is not

- It covers **code-level look-ahead**: a script's output at time t depends on data after t.
  It does not cover LLM-knowledge leakage (a model that remembers the future); that is what
  Look-Ahead-Bench measures. It also leaves out ML train/test leakage that has no time
  dimension.
- The scripts are **synthetic and small** (6 to 37 lines), in a neutral style without vendor
  APIs, suggestive names or a pnl line. Rates describe this corpus, not code in the wild, and
  rules keyed to those forms have nothing to match here.
- A **leak label is a proof**: the oracle produces a concrete witness (cut t, perturbation,
  row). A **clean label is evidence**: no tried perturbation moved the past. Because the oracle
  admits files, leaks it cannot witness are absent. See
  [docs/DESIGN.md](docs/DESIGN.md) for the soundness argument and its limits.
- **Static tools only.** Several of these tools also ship runtime checks, which are not scored.
- **v1 is frozen.** Tools may be tuned on a public corpus, and a fresh generator seed only
  changes names and window lengths. Fresh seeds 101 and 202 give nearly the same scorecard
  ([results/fresh](results/fresh)), which shows the rates do not hang on those choices. It takes
  new templates to reveal tuning.

## Quick start

```sh
uv sync                                  # project + pinned linters (dev group)
uv run leakseed generate --check         # v1 matches its manifest and regenerates byte for byte
uv run leakseed verify --workers 3       # oracle on all 368 files (a few minutes)
uv run leakseed impact                   # Sharpe of each file on drift-free data (under a minute)
uv run leakseed score --tool all         # run the linters, store findings
uv run leakseed report                   # results/v1/summary.json + scorecard.md
uv run python scripts/probes.py          # results/v1/probes.md
uv run leakseed generate --seed 7 --out tmp/c7   # a fresh corpus from another seed
```

`verify` and `impact` import only corpus files whose SHA-256 matches the manifest. The linters
run statically (no tool executes corpus code). No network or model calls at run time.

## Layout

| Path | What |
|---|---|
| `src/leakseed/templates/` | rendering framework (`core.py`) and the 15 leak classes (`classes.py`) |
| `src/leakseed/data.py` | synthetic market data and the after-t perturbations |
| `src/leakseed/oracle.py` | causality oracle and `verify` |
| `src/leakseed/impact.py` | Sharpe of each file on drift-free data |
| `src/leakseed/adapters/` | one adapter per linter, output -> (file, line, rule, severity) |
| `src/leakseed/score.py`, `stats.py`, `report.py` | estimands, intervals, tests, scorecard |
| `corpus/v1/` | frozen corpus: `files/`, `manifest.jsonl`, `VERSION.json` |
| `corpus/probes/` | hand-written pairs for rules the v1 style cannot trigger |
| `results/v1/` | oracle verdicts, tool findings, impact, `summary.json`, `scorecard.md`, `probes.md` |
| `results/fresh/` | scorecards of two fresh generator seeds |
| `docs/DESIGN.md` | taxonomy, oracle soundness, statistics, threat model, tool vetting, prior art |
| `docs/upstream/` | draft issues for the linters (not filed) |

## Citing

See [CITATION.cff](CITATION.cff). MIT licence.
