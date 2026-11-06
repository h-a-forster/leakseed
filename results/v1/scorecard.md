# Scorecard (corpus seed 20261030)

Corpus: 368 files = 184 leak/clean pairs, 15 classes, 30 templates. Oracle: 368/368 labels confirmed (9952 script runs, n = 5000 rows, 16 cut points x 3 perturbation modes).
Intervals: pooled rates use a cluster bootstrap over templates (10000 resamples, percentile 95%); per-cell rates use Clopper-Pearson 95%.

## Headline (each tool's documented leakage rules)

| Tool | Version | Recall | False-positive rate | Paired discrimination | Localisation |
|---|---|---|---|---|---|
| lookahead-lint | 1.0.1 | 7.6% [2.3, 14.7] (14/184) | 2.2% [0.0, 6.2] (4/184) | 5.4% [1.8, 9.8] (10/184) | 100.0% [100.0, 100.0] (14/14) |
| peekproof | 0.1.0+e6c56c3 | 21.2% [10.6, 32.7] (39/184) | 3.8% [1.1, 6.9] (7/184) | 17.4% [9.1, 26.1] (32/184) | 100.0% [100.0, 100.0] (39/39) |
| backtest-audit | 1.0.0 | 4.3% [0.0, 11.1] (8/184) | 2.2% [0.0, 7.3] (4/184) | 2.2% [0.0, 7.0] (4/184) | 100.0% [100.0, 100.0] (8/8) |
| leakguard | 0.1.1 | 17.4% [8.5, 27.7] (32/184) | 6.0% [1.3, 12.2] (11/184) | 11.4% [5.5, 18.2] (21/184) | 100.0% [100.0, 100.0] (32/32) |
| ruff-defaults | 0.17.1 | 0.0% [0.0, 0.0] (0/184) | 0.0% [0.0, 0.0] (0/184) | 0.0% [0.0, 0.0] (0/184) | n/a (0 files) |
| any of the four linters | - | 34.2% [21.5, 47.4] (63/184) | 11.4% [4.6, 19.4] (21/184) | 22.8% [13.8, 32.1] (42/184) | - |

## Sensitivity: every rule counts

| Tool | Recall | False-positive rate | Paired discrimination |
|---|---|---|---|
| lookahead-lint | 7.6% [2.3, 14.7] (14/184) | 2.2% [0.0, 6.2] (4/184) | 5.4% [1.8, 9.8] (10/184) |
| peekproof | 21.2% [10.6, 32.7] (39/184) | 3.8% [1.1, 6.9] (7/184) | 17.4% [9.1, 26.1] (32/184) |
| backtest-audit | 100.0% [100.0, 100.0] (184/184) | 100.0% [100.0, 100.0] (184/184) | 0.0% [0.0, 0.0] (0/184) |
| leakguard | 17.4% [8.5, 27.7] (32/184) | 6.0% [1.3, 12.2] (11/184) | 11.4% [5.5, 18.2] (21/184) |
| ruff-defaults | 0.0% [0.0, 0.0] (0/184) | 0.0% [0.0, 0.0] (0/184) | 0.0% [0.0, 0.0] (0/184) |

## Recall by obfuscation level (Clopper-Pearson)

| Tool | L0 | L1 | L2 | L3 |
|---|---|---|---|---|
| lookahead-lint | 17.4% [7.8, 31.4] (8/46) | 4.3% [0.5, 14.8] (2/46) | 4.3% [0.5, 14.8] (2/46) | 4.3% [0.5, 14.8] (2/46) |
| peekproof | 43.5% [28.9, 58.9] (20/46) | 13.0% [4.9, 26.3] (6/46) | 13.0% [4.9, 26.3] (6/46) | 15.2% [6.3, 28.9] (7/46) |
| backtest-audit | 6.5% [1.4, 17.9] (3/46) | 6.5% [1.4, 17.9] (3/46) | 2.2% [0.1, 11.5] (1/46) | 2.2% [0.1, 11.5] (1/46) |
| leakguard | 26.1% [14.3, 41.1] (12/46) | 21.7% [10.9, 36.4] (10/46) | 10.9% [3.6, 23.6] (5/46) | 10.9% [3.6, 23.6] (5/46) |
| ruff-defaults | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) |

## Paired discrimination by obfuscation level (Clopper-Pearson)

| Tool | L0 | L1 | L2 | L3 |
|---|---|---|---|---|
| lookahead-lint | 17.4% [7.8, 31.4] (8/46) | 2.2% [0.1, 11.5] (1/46) | 2.2% [0.1, 11.5] (1/46) | 0.0% [0.0, 7.7] (0/46) |
| peekproof | 43.5% [28.9, 58.9] (20/46) | 13.0% [4.9, 26.3] (6/46) | 13.0% [4.9, 26.3] (6/46) | 0.0% [0.0, 7.7] (0/46) |
| backtest-audit | 4.3% [0.5, 14.8] (2/46) | 4.3% [0.5, 14.8] (2/46) | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) |
| leakguard | 26.1% [14.3, 41.1] (12/46) | 15.2% [6.3, 28.9] (7/46) | 4.3% [0.5, 14.8] (2/46) | 0.0% [0.0, 7.7] (0/46) |
| ruff-defaults | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) |

## Recall by library

| Tool | pandas | numpy | polars |
|---|---|---|---|
| lookahead-lint | 13.0% [7.1, 21.2] (13/100) | 0.0% [0.0, 9.7] (0/36) | 2.1% [0.1, 11.1] (1/48) |
| peekproof | 20.0% [12.7, 29.2] (20/100) | 0.0% [0.0, 9.7] (0/36) | 39.6% [25.8, 54.7] (19/48) |
| backtest-audit | 2.0% [0.2, 7.0] (2/100) | 11.1% [3.1, 26.1] (4/36) | 4.2% [0.5, 14.3] (2/48) |
| leakguard | 26.0% [17.7, 35.7] (26/100) | 11.1% [3.1, 26.1] (4/36) | 4.2% [0.5, 14.3] (2/48) |
| ruff-defaults | 0.0% [0.0, 3.6] (0/100) | 0.0% [0.0, 9.7] (0/36) | 0.0% [0.0, 7.4] (0/48) |

## Per-class heatmap: recall, leaky files flagged / leaky files

Shading: blank 0, ░ < 25%, ▒ < 50%, ▓ < 75%, █ >= 75%. Last column: levels at which at least one linter flags at least one leaky file.

| Class | lookahead-lint | peekproof | backtest-audit | leakguard | caught at |
|---|---|---|---|---|---|
| same_bar |   0/20 |   0/20 |   0/20 |   0/20 | none |
| negative_shift | ░ 2/12 | ▒ 3/12 | ▒ 4/12 | ▓ 6/12 | L0, L1 |
| centered_rolling | ░ 2/16 | ▒ 4/16 |   0/16 | ▒ 4/16 | L0, L1 |
| full_sample_scaling |   0/16 | ▓ 8/16 | ▒ 4/16 |   0/16 | L0, L1, L2, L3 |
| backfill_interpolate | ▒ 4/16 | █ 13/16 |   0/16 | ▒ 4/16 | L0, L1, L2, L3 |
| resample_label |   0/12 | ░ 1/12 |   0/12 | ▓ 8/12 | L0, L1, L2, L3 |
| asof_forward | ░ 2/12 | ▒ 3/12 |   0/12 | ░ 2/12 | L0 |
| fundamentals_period_end |   0/12 | ░ 2/12 |   0/12 |   0/12 | L0 |
| restatement_overwrite |   0/8 |   0/8 |   0/8 |   0/8 | none |
| survivorship |   0/8 |   0/8 |   0/8 |   0/8 | none |
| shuffled_split | ▓ 4/8 | ░ 1/8 |   0/8 | █ 8/8 | L0, L1, L2, L3 |
| groupby_transform |   0/12 | ▒ 4/12 |   0/12 |   0/12 | L0, L1, L2, L3 |
| np_roll |   0/8 |   0/8 |   0/8 |   0/8 | none |
| reversed_cumulative |   0/16 |   0/16 |   0/16 |   0/16 | none |
| argmax_param |   0/8 |   0/8 |   0/8 |   0/8 | none |

## False positives by class (clean twins flagged / clean twins)

| Class | lookahead-lint | peekproof | backtest-audit | leakguard |
|---|---|---|---|---|
| same_bar | 0 | 0 | 0 | 0 |
| negative_shift | 0 | 0 | 0 | 0 |
| centered_rolling | 0 | 0 | 0 | 0 |
| full_sample_scaling | 0 | 2/16 | 4/16 | 0 |
| backfill_interpolate | 1/16 | 3/16 | 0 | 1/16 |
| resample_label | 0 | 1/12 | 0 | 6/12 |
| asof_forward | 0 | 0 | 0 | 0 |
| fundamentals_period_end | 0 | 0 | 0 | 0 |
| restatement_overwrite | 0 | 0 | 0 | 0 |
| survivorship | 0 | 0 | 0 | 0 |
| shuffled_split | 3/8 | 0 | 0 | 4/8 |
| groupby_transform | 0 | 1/12 | 0 | 0 |
| np_roll | 0 | 0 | 0 | 0 |
| reversed_cumulative | 0 | 0 | 0 | 0 |
| argmax_param | 0 | 0 | 0 | 0 |

## Paired tool comparisons (exact McNemar, Holm over all rows)

| A | B | Measure | only A | only B | p | p (Holm) |
|---|---|---|---|---|---|---|
| lookahead-lint | peekproof | recall | 3 | 28 | 4.65e-06 | 4.18e-05 |
| lookahead-lint | peekproof | paired | 0 | 22 | 4.77e-07 | 5.25e-06 |
| lookahead-lint | backtest-audit | recall | 12 | 6 | 0.238 | 0.476 |
| lookahead-lint | backtest-audit | paired | 8 | 2 | 0.109 | 0.328 |
| lookahead-lint | leakguard | recall | 0 | 18 | 7.63e-06 | 6.1e-05 |
| lookahead-lint | leakguard | paired | 0 | 11 | 0.000977 | 0.00488 |
| peekproof | backtest-audit | recall | 37 | 6 | 1.64e-06 | 1.64e-05 |
| peekproof | backtest-audit | paired | 30 | 2 | 2.46e-07 | 2.96e-06 |
| peekproof | leakguard | recall | 27 | 20 | 0.382 | 0.476 |
| peekproof | leakguard | paired | 21 | 10 | 0.0708 | 0.283 |
| backtest-audit | leakguard | recall | 4 | 28 | 1.93e-05 | 0.000116 |
| backtest-audit | leakguard | paired | 0 | 17 | 1.53e-05 | 0.000107 |

## Coverage

Classes no linter flags at any level: same_bar, restatement_overwrite, survivorship, np_roll, reversed_cumulative, argmax_param.

## False positives (clean twins flagged, file:line rule)

- lookahead-lint: `files/f421ec9900a.py:10` LA002 (backfill_interpolate, L3, pandas)
- lookahead-lint: `files/f518d028dc7.py:11` LA005 (shuffled_split, L3, pandas)
- lookahead-lint: `files/f646bb135d7.py:7` LA005 (shuffled_split, L2, pandas)
- lookahead-lint: `files/fcd1b3331e2.py:14` LA005 (shuffled_split, L1, pandas)
- peekproof: `files/f058a6adc75.py:10` PP002 (backfill_interpolate, L3, polars)
- peekproof: `files/f1ae6c81230.py:10` PP002 (backfill_interpolate, L3, pandas)
- peekproof: `files/f421ec9900a.py:10` PP002 (backfill_interpolate, L3, pandas)
- peekproof: `files/f7e63712502.py:8` PP006 (full_sample_scaling, L3, pandas)
- peekproof: `files/fab999f2155.py:10` PP006 (full_sample_scaling, L3, polars)
- peekproof: `files/fc240e5ca82.py:10` PP006 (groupby_transform, L3, polars)
- peekproof: `files/feaf443153a.py:16` PP011 (resample_label, L3, polars)
- backtest-audit: `files/f3be90a6d5e.py:6` LEAK001 (full_sample_scaling, L2, numpy)
- backtest-audit: `files/f61fe3095bc.py:11` LEAK001 (full_sample_scaling, L0, numpy)
- backtest-audit: `files/fb10e84acdd.py:10` LEAK001 (full_sample_scaling, L3, numpy)
- backtest-audit: `files/fd48908136e.py:12` LEAK001 (full_sample_scaling, L1, numpy)
- leakguard: `files/f032dfffef6.py:11` LG004 (shuffled_split, L3, numpy)
- leakguard: `files/f22f084523f.py:9` LG009 (resample_label, L3, pandas)
- leakguard: `files/f3c3c9cf9de.py:5` LG009 (resample_label, L2, pandas)
- leakguard: `files/f421ec9900a.py:10` LG007 (backfill_interpolate, L3, pandas)
- leakguard: `files/f4da5e44a18.py:9` LG009 (resample_label, L1, pandas)
- leakguard: `files/f518d028dc7.py:11` LG004 (shuffled_split, L3, pandas)
- leakguard: `files/f646bb135d7.py:7` LG004 (shuffled_split, L2, pandas)
- leakguard: `files/f6533b240b9.py:5` LG009 (resample_label, L2, pandas)
- leakguard: `files/fbaa8a4f35d.py:9` LG009 (resample_label, L3, pandas)
- leakguard: `files/fcd1b3331e2.py:14` LG004 (shuffled_split, L1, pandas)
- leakguard: `files/fce33998f64.py:7` LG009 (resample_label, L1, pandas)

## Leaky L0 files no linter flags (file:site lines)

- `files/f0494aafcfb.py:12` (same_bar, numpy)
- `files/f07bd3722e6.py:8,9,10` (np_roll, numpy)
- `files/f12808039d4.py:4` (fundamentals_period_end, pandas)
- `files/f178169036d.py:12` (argmax_param, numpy)
- `files/f18085e9e7b.py:12` (same_bar, numpy)
- `files/f1be6836bcb.py:8` (reversed_cumulative, pandas)
- `files/f1d832b7418.py:9` (np_roll, numpy)
- `files/f221fd1c552.py:7` (same_bar, pandas)
- `files/f2dec227339.py:5` (groupby_transform, pandas)
- `files/f308bb96359.py:6` (survivorship, pandas)
- `files/f33b0d845ba.py:4,5` (restatement_overwrite, pandas)
- `files/f3faf8c1f46.py:8` (reversed_cumulative, numpy)
- `files/f416142bd2a.py:7` (resample_label, polars)
- `files/f4435c06ba7.py:13` (argmax_param, pandas)
- `files/f463f8bb8aa.py:4` (restatement_overwrite, pandas)
- `files/f55918d6c13.py:5` (survivorship, pandas)
- `files/f746a45724e.py:5` (groupby_transform, pandas)
- `files/f87b0f00ff6.py:8` (same_bar, polars)
- `files/fa2c5cb558a.py:3` (reversed_cumulative, pandas)
- `files/fd2a43a0eef.py:9` (full_sample_scaling, numpy)
- `files/fd5996b1360.py:8` (same_bar, pandas)
- `files/fd6baad3d7c.py:7` (reversed_cumulative, polars)
