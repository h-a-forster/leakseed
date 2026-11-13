# leakseed 0.1.0 release notes

First release, tagged v0.1.0 and published on 2026-11-08. Results are in [results/v1/scorecard.md](../results/v1/scorecard.md) and
`results/fresh/`.

## What it does

leakseed is a seeded corpus of look-ahead leaks in small backtest scripts, in leak/clean twin
pairs, and a scorecard of static leakage linters on it. Each label is verified by running the
script under a causality oracle. Linters run statically; no model or network calls at run
time.

## In this release

- Corpus v1: 368 scripts = 184 pairs, 15 leak classes x 4 obfuscation levels x pandas, numpy and
  polars, from 30 templates, with a JSONL manifest of site lines.
- Causality oracle with three perturbation modes, witnesses for every leak verdict, and
  refusal on malformed, nondeterministic or vacuous output.
- Adapters for seven linters (lookahead-lint, peekproof, backtest-audit, leakguard,
  overfit-gauntlet, monte-neo, nofuturedata) and a ruff null baseline.
- Scorecard: recall, false-positive rate, file-level pairing and pairing at the site, with
  template-clustered bootstrap intervals, Clopper-Pearson cells, an exact template sign-flip
  test with Holm adjustment, localisation against a random line, severity and any-rule
  sensitivities, and the Sharpe each file earns on drift-free data.
- `corpus/probes`: three hand-written pairs showing what rules outside the v1 style do.
- `docs/upstream/`: four draft issues for the linters, none filed at release (one filed
  since; see [upstream.md](upstream.md)).

## Corrections made before the release

Each of these changed an earlier result, and each has a test that fails without it.

- Events stamped on day t were treated as unknown at the close of day t, so a causal script
  could get a false leak verdict.
- The cut grid spent half its cuts before the first output of scripts that trade the second
  half, and a leaky argmax file passed as clean on one data seed.
- At L3 the dead leaky branch counted as a hit at the site unless the twin check covered both
  files' site lines.
- Sharpe used simple returns, whose mean is positive on a driftless log-price walk, so long
  positions showed a small gain. It now uses log returns. 61 leaky files stay material, and the
  largest clean twin moves from 0.20 to 0.19.
- The any-linter row took paired discrimination from the union of flags while its other columns
  were an OR over tools. All columns are now an OR over tools: 54/184 becomes 70/184.

## Other fixes from the audits

- The build needs `hatchling>=1.26`: the PEP 639 `license-files` list fails on older versions.
- `verify`, `impact`, `score` and `report` refuse a results directory that belongs to another
  corpus (`corpus.json`), so a forgotten `--out` cannot overwrite `results/v1`.
- `summary.json` is strict JSON: an empty rate is `null`, not `NaN`.
- The oracle refuses an output that has neither one column nor one per asset.
