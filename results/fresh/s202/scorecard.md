# Scorecard (corpus seed 202)

Corpus: 368 files = 184 leak/clean pairs, 15 classes, 30 templates. Oracle: 368/368 labels confirmed (9867 script runs, n = 5000 rows, 16 cut points x 3 perturbation modes).
Intervals: pooled rates use a cluster bootstrap over templates (10000 resamples, percentile 95%); per-cell rates use Clopper-Pearson 95%.

## Headline (each tool's documented leakage rules)

| Tool | Version | Recall | False-positive rate | Paired discrimination | Paired at the site |
|---|---|---|---|---|---|
| lookahead-lint | 1.0.1 | 7.6% [2.3, 14.7] (14/184) | 2.2% [0.0, 6.2] (4/184) | 5.4% [1.8, 9.8] (10/184) | 5.4% [1.8, 9.8] (10/184) |
| peekproof | 0.1.0+e6c56c3 | 21.7% [11.0, 33.2] (40/184) | 4.3% [1.1, 7.9] (8/184) | 17.4% [9.1, 26.1] (32/184) | 17.4% [9.1, 26.1] (32/184) |
| backtest-audit | 1.0.0 | 4.3% [0.0, 11.1] (8/184) | 2.2% [0.0, 7.3] (4/184) | 2.2% [0.0, 7.0] (4/184) | 2.2% [0.0, 7.0] (4/184) |
| leakguard | 0.1.1 | 17.4% [8.5, 27.7] (32/184) | 6.0% [1.3, 12.2] (11/184) | 11.4% [5.5, 18.2] (21/184) | 11.4% [5.5, 18.2] (21/184) |
| overfit-gauntlet | 0.1.0 | 11.4% [4.1, 19.9] (21/184) | 4.9% [0.5, 10.6] (9/184) | 6.5% [2.1, 12.0] (12/184) | 6.5% [2.1, 12.0] (12/184) |
| monte-neo | 0.54.0 | 57.6% [44.6, 71.1] (106/184) | 31.5% [19.1, 46.4] (58/184) | 26.1% [15.9, 36.0] (48/184) | 33.2% [22.9, 43.4] (61/184) |
| nofuturedata | 0.5.0.dev0+fb46880 | 14.1% [6.7, 23.8] (26/184) | 2.2% [0.5, 4.5] (4/184) | 12.0% [6.1, 19.2] (22/184) | 12.0% [6.1, 19.2] (22/184) |
| ruff-defaults | 0.17.1 | 0.0% [0.0, 0.0] (0/184) | 0.0% [0.0, 0.0] (0/184) | 0.0% [0.0, 0.0] (0/184) | 0.0% [0.0, 0.0] (0/184) |
| any linter | - | 65.8% [51.5, 79.8] (121/184) | 36.4% [23.3, 51.6] (67/184) | 29.3% [18.5, 39.7] (54/184) | 39.7% [28.6, 50.5] (73/184) |

## Balanced over classes

Pooled rates weight classes by their file counts. These are means of class rates.

| Tool | Recall | Paired at the site |
|---|---|---|
| lookahead-lint | 8.1% | 5.1% |
| peekproof | 19.0% | 15.3% |
| backtest-audit | 3.9% | 2.2% |
| leakguard | 18.9% | 11.8% |
| overfit-gauntlet | 12.5% | 7.1% |
| monte-neo | 61.1% | 33.1% |
| nofuturedata | 17.2% | 14.3% |

## Localisation (leaky files flagged)

Within 2 lines of a site line, on a site line, and what a random code line of the same files would score within 2 lines.

| Tool | Within 2 lines | On a site line | Random line within 2 |
|---|---|---|---|
| lookahead-lint | 14/14 | 14/14 | 52% |
| peekproof | 40/40 | 40/40 | 59% |
| backtest-audit | 8/8 | 8/8 | 54% |
| leakguard | 32/32 | 32/32 | 56% |
| overfit-gauntlet | 21/21 | 21/21 | 53% |
| monte-neo | 92/106 | 92/106 | 58% |
| nofuturedata | 26/26 | 26/26 | 57% |

## Sensitivity: the tool's top severity only

Tools without grades are unchanged (peekproof high, leakguard error, overfit-gauntlet error, monte-neo fail).

| Tool | Recall | False-positive rate | Paired at the site |
|---|---|---|---|
| peekproof | 8.7% [3.2, 15.3] (16/184) | 0.5% [0.0, 1.7] (1/184) | 8.2% [3.2, 14.0] (15/184) |
| leakguard | 13.0% [5.4, 22.2] (24/184) | 2.7% [0.0, 7.0] (5/184) | 10.3% [4.3, 17.3] (19/184) |
| overfit-gauntlet | 7.1% [1.7, 14.0] (13/184) | 2.2% [0.0, 6.2] (4/184) | 4.9% [1.5, 9.1] (9/184) |
| monte-neo | 27.7% [15.3, 41.3] (51/184) | 4.3% [1.4, 7.8] (8/184) | 23.4% [13.3, 34.0] (43/184) |

## Sensitivity: every rule counts

| Tool | Recall | False-positive rate | Paired at the site |
|---|---|---|---|
| lookahead-lint | 7.6% [2.3, 14.7] (14/184) | 2.2% [0.0, 6.2] (4/184) | 5.4% [1.8, 9.8] (10/184) |
| peekproof | 21.7% [11.0, 33.2] (40/184) | 4.3% [1.1, 7.9] (8/184) | 17.4% [9.1, 26.1] (32/184) |
| backtest-audit | 100.0% [100.0, 100.0] (184/184) | 100.0% [100.0, 100.0] (184/184) | 2.2% [0.0, 7.0] (4/184) |
| leakguard | 17.4% [8.5, 27.7] (32/184) | 6.0% [1.3, 12.2] (11/184) | 11.4% [5.5, 18.2] (21/184) |
| overfit-gauntlet | 11.4% [4.1, 19.9] (21/184) | 4.9% [0.5, 10.6] (9/184) | 6.5% [2.1, 12.0] (12/184) |
| monte-neo | 57.6% [44.6, 71.1] (106/184) | 31.5% [19.1, 46.4] (58/184) | 33.2% [22.9, 43.4] (61/184) |
| nofuturedata | 14.1% [6.7, 23.8] (26/184) | 2.2% [0.5, 4.5] (4/184) | 12.0% [6.1, 19.2] (22/184) |
| ruff-defaults | 0.0% [0.0, 0.0] (0/184) | 0.0% [0.0, 0.0] (0/184) | 0.0% [0.0, 0.0] (0/184) |

## Recall by obfuscation level (Clopper-Pearson)

| Tool | L0 | L1 | L2 | L3 |
|---|---|---|---|---|
| lookahead-lint | 17.4% [7.8, 31.4] (8/46) | 4.3% [0.5, 14.8] (2/46) | 4.3% [0.5, 14.8] (2/46) | 4.3% [0.5, 14.8] (2/46) |
| peekproof | 43.5% [28.9, 58.9] (20/46) | 13.0% [4.9, 26.3] (6/46) | 13.0% [4.9, 26.3] (6/46) | 17.4% [7.8, 31.4] (8/46) |
| backtest-audit | 6.5% [1.4, 17.9] (3/46) | 6.5% [1.4, 17.9] (3/46) | 2.2% [0.1, 11.5] (1/46) | 2.2% [0.1, 11.5] (1/46) |
| leakguard | 26.1% [14.3, 41.1] (12/46) | 21.7% [10.9, 36.4] (10/46) | 10.9% [3.6, 23.6] (5/46) | 10.9% [3.6, 23.6] (5/46) |
| overfit-gauntlet | 19.6% [9.4, 33.9] (9/46) | 8.7% [2.4, 20.8] (4/46) | 8.7% [2.4, 20.8] (4/46) | 8.7% [2.4, 20.8] (4/46) |
| monte-neo | 67.4% [52.0, 80.5] (31/46) | 67.4% [52.0, 80.5] (31/46) | 47.8% [32.9, 63.1] (22/46) | 47.8% [32.9, 63.1] (22/46) |
| nofuturedata | 30.4% [17.7, 45.8] (14/46) | 8.7% [2.4, 20.8] (4/46) | 8.7% [2.4, 20.8] (4/46) | 8.7% [2.4, 20.8] (4/46) |
| ruff-defaults | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) |

## False-positive rate by obfuscation level (Clopper-Pearson)

Both L3 twins contain the leaky expression in a branch the config turns off.

| Tool | L0 | L1 | L2 | L3 |
|---|---|---|---|---|
| lookahead-lint | 0.0% [0.0, 7.7] (0/46) | 2.2% [0.1, 11.5] (1/46) | 2.2% [0.1, 11.5] (1/46) | 4.3% [0.5, 14.8] (2/46) |
| peekproof | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) | 17.4% [7.8, 31.4] (8/46) |
| backtest-audit | 2.2% [0.1, 11.5] (1/46) | 2.2% [0.1, 11.5] (1/46) | 2.2% [0.1, 11.5] (1/46) | 2.2% [0.1, 11.5] (1/46) |
| leakguard | 0.0% [0.0, 7.7] (0/46) | 6.5% [1.4, 17.9] (3/46) | 6.5% [1.4, 17.9] (3/46) | 10.9% [3.6, 23.6] (5/46) |
| overfit-gauntlet | 2.2% [0.1, 11.5] (1/46) | 4.3% [0.5, 14.8] (2/46) | 4.3% [0.5, 14.8] (2/46) | 8.7% [2.4, 20.8] (4/46) |
| monte-neo | 26.1% [14.3, 41.1] (12/46) | 26.1% [14.3, 41.1] (12/46) | 26.1% [14.3, 41.1] (12/46) | 47.8% [32.9, 63.1] (22/46) |
| nofuturedata | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) | 8.7% [2.4, 20.8] (4/46) |
| ruff-defaults | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) |

## Paired discrimination by obfuscation level (Clopper-Pearson)

| Tool | L0 | L1 | L2 | L3 |
|---|---|---|---|---|
| lookahead-lint | 17.4% [7.8, 31.4] (8/46) | 2.2% [0.1, 11.5] (1/46) | 2.2% [0.1, 11.5] (1/46) | 0.0% [0.0, 7.7] (0/46) |
| peekproof | 43.5% [28.9, 58.9] (20/46) | 13.0% [4.9, 26.3] (6/46) | 13.0% [4.9, 26.3] (6/46) | 0.0% [0.0, 7.7] (0/46) |
| backtest-audit | 4.3% [0.5, 14.8] (2/46) | 4.3% [0.5, 14.8] (2/46) | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) |
| leakguard | 26.1% [14.3, 41.1] (12/46) | 15.2% [6.3, 28.9] (7/46) | 4.3% [0.5, 14.8] (2/46) | 0.0% [0.0, 7.7] (0/46) |
| overfit-gauntlet | 17.4% [7.8, 31.4] (8/46) | 4.3% [0.5, 14.8] (2/46) | 4.3% [0.5, 14.8] (2/46) | 0.0% [0.0, 7.7] (0/46) |
| monte-neo | 41.3% [27.0, 56.8] (19/46) | 41.3% [27.0, 56.8] (19/46) | 21.7% [10.9, 36.4] (10/46) | 0.0% [0.0, 7.7] (0/46) |
| nofuturedata | 30.4% [17.7, 45.8] (14/46) | 8.7% [2.4, 20.8] (4/46) | 8.7% [2.4, 20.8] (4/46) | 0.0% [0.0, 7.7] (0/46) |
| ruff-defaults | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) |

## Paired at the site by obfuscation level (Clopper-Pearson)

| Tool | L0 | L1 | L2 | L3 |
|---|---|---|---|---|
| lookahead-lint | 17.4% [7.8, 31.4] (8/46) | 2.2% [0.1, 11.5] (1/46) | 2.2% [0.1, 11.5] (1/46) | 0.0% [0.0, 7.7] (0/46) |
| peekproof | 43.5% [28.9, 58.9] (20/46) | 13.0% [4.9, 26.3] (6/46) | 13.0% [4.9, 26.3] (6/46) | 0.0% [0.0, 7.7] (0/46) |
| backtest-audit | 4.3% [0.5, 14.8] (2/46) | 4.3% [0.5, 14.8] (2/46) | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) |
| leakguard | 26.1% [14.3, 41.1] (12/46) | 15.2% [6.3, 28.9] (7/46) | 4.3% [0.5, 14.8] (2/46) | 0.0% [0.0, 7.7] (0/46) |
| overfit-gauntlet | 17.4% [7.8, 31.4] (8/46) | 4.3% [0.5, 14.8] (2/46) | 4.3% [0.5, 14.8] (2/46) | 0.0% [0.0, 7.7] (0/46) |
| monte-neo | 52.2% [36.9, 67.1] (24/46) | 52.2% [36.9, 67.1] (24/46) | 28.3% [16.0, 43.5] (13/46) | 0.0% [0.0, 7.7] (0/46) |
| nofuturedata | 30.4% [17.7, 45.8] (14/46) | 8.7% [2.4, 20.8] (4/46) | 8.7% [2.4, 20.8] (4/46) | 0.0% [0.0, 7.7] (0/46) |
| ruff-defaults | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) |

## Recall by library

| Tool | pandas | numpy | polars |
|---|---|---|---|
| lookahead-lint | 13.0% [7.1, 21.2] (13/100) | 0.0% [0.0, 9.7] (0/36) | 2.1% [0.1, 11.1] (1/48) |
| peekproof | 21.0% [13.5, 30.3] (21/100) | 0.0% [0.0, 9.7] (0/36) | 39.6% [25.8, 54.7] (19/48) |
| backtest-audit | 2.0% [0.2, 7.0] (2/100) | 11.1% [3.1, 26.1] (4/36) | 4.2% [0.5, 14.3] (2/48) |
| leakguard | 26.0% [17.7, 35.7] (26/100) | 11.1% [3.1, 26.1] (4/36) | 4.2% [0.5, 14.3] (2/48) |
| overfit-gauntlet | 16.0% [9.4, 24.7] (16/100) | 11.1% [3.1, 26.1] (4/36) | 2.1% [0.1, 11.1] (1/48) |
| monte-neo | 76.0% [66.4, 84.0] (76/100) | 44.4% [27.9, 61.9] (16/36) | 29.2% [17.0, 44.1] (14/48) |
| nofuturedata | 21.0% [13.5, 30.3] (21/100) | 11.1% [3.1, 26.1] (4/36) | 2.1% [0.1, 11.1] (1/48) |
| ruff-defaults | 0.0% [0.0, 3.6] (0/100) | 0.0% [0.0, 9.7] (0/36) | 0.0% [0.0, 7.4] (0/48) |

## Per-class heatmap: recall, leaky files flagged / leaky files

Shading: blank 0, ░ < 25%, ▒ < 50%, ▓ < 75%, █ >= 75%.

| Class | lookahead-lint | peekproof | backtest-audit | leakguard | overfit-gauntlet | monte-neo | nofuturedata |
|---|---|---|---|---|---|---|---|
| same_bar |   0/20 |   0/20 |   0/20 |   0/20 |   0/20 |   0/20 |   0/20 |
| negative_shift | ░ 2/12 | ▒ 3/12 | ▒ 4/12 | ▓ 6/12 | ▒ 3/12 | ▓ 6/12 | ▒ 3/12 |
| centered_rolling | ░ 2/16 | ▒ 4/16 |   0/16 | ▒ 4/16 | ░ 2/16 | ▓ 8/16 | ░ 2/16 |
| full_sample_scaling |   0/16 | ▓ 8/16 | ▒ 4/16 |   0/16 | ▒ 4/16 | ▓ 8/16 |   0/16 |
| backfill_interpolate | ▒ 4/16 | █ 13/16 |   0/16 | ▒ 4/16 | ▒ 4/16 | █ 12/16 | ▒ 4/16 |
| resample_label |   0/12 | ░ 2/12 |   0/12 | ▓ 8/12 |   0/12 | █ 12/12 | ░ 2/12 |
| asof_forward | ░ 2/12 | ▒ 3/12 |   0/12 | ░ 2/12 |   0/12 | ▒ 4/12 | ░ 2/12 |
| fundamentals_period_end |   0/12 | ░ 2/12 |   0/12 |   0/12 |   0/12 | ▓ 8/12 |   0/12 |
| restatement_overwrite |   0/8 |   0/8 |   0/8 |   0/8 |   0/8 | █ 8/8 |   0/8 |
| survivorship |   0/8 |   0/8 |   0/8 |   0/8 |   0/8 | █ 8/8 | █ 8/8 |
| shuffled_split | ▓ 4/8 | ░ 1/8 |   0/8 | █ 8/8 | █ 8/8 | █ 8/8 | ▓ 5/8 |
| groupby_transform |   0/12 | ▒ 4/12 |   0/12 |   0/12 |   0/12 | ▓ 8/12 |   0/12 |
| np_roll |   0/8 |   0/8 |   0/8 |   0/8 |   0/8 |   0/8 |   0/8 |
| reversed_cumulative |   0/16 |   0/16 |   0/16 |   0/16 |   0/16 | █ 12/16 |   0/16 |
| argmax_param |   0/8 |   0/8 |   0/8 |   0/8 |   0/8 | ▓ 4/8 |   0/8 |

## Per-class heatmap: paired at the site

Pairs with a flag on a site line of the leaky file and none at the same place in its twin. Last column: levels where at least one linter does this.

| Class | lookahead-lint | peekproof | backtest-audit | leakguard | overfit-gauntlet | monte-neo | nofuturedata | found at |
|---|---|---|---|---|---|---|---|---|
| same_bar |   0/20 |   0/20 |   0/20 |   0/20 |   0/20 |   0/20 |   0/20 | none |
| negative_shift | ░ 2/12 | ▒ 3/12 | ▒ 4/12 | ▓ 6/12 | ▒ 3/12 | ▓ 6/12 | ▒ 3/12 | L0, L1 |
| centered_rolling | ░ 2/16 | ▒ 4/16 |   0/16 | ▒ 4/16 | ░ 2/16 | ▓ 8/16 | ░ 2/16 | L0, L1 |
| full_sample_scaling |   0/16 | ▒ 6/16 |   0/16 |   0/16 |   0/16 | ▒ 6/16 |   0/16 | L0, L1, L2 |
| backfill_interpolate | ░ 3/16 | ▓ 10/16 |   0/16 | ░ 3/16 | ░ 3/16 | ▓ 9/16 | ░ 3/16 | L0, L1, L2 |
| resample_label |   0/12 |   0/12 |   0/12 | ░ 2/12 |   0/12 |   0/12 | ░ 2/12 | L0 |
| asof_forward | ░ 2/12 | ▒ 3/12 |   0/12 | ░ 2/12 |   0/12 | ▒ 4/12 | ░ 2/12 | L0, L1 |
| fundamentals_period_end |   0/12 | ░ 2/12 |   0/12 |   0/12 |   0/12 |   0/12 |   0/12 | L0 |
| restatement_overwrite |   0/8 |   0/8 |   0/8 |   0/8 |   0/8 | ▒ 2/8 |   0/8 | L0, L1 |
| survivorship |   0/8 |   0/8 |   0/8 |   0/8 |   0/8 | █ 6/8 | █ 6/8 | L0, L1, L2 |
| shuffled_split | ░ 1/8 | ░ 1/8 |   0/8 | ▓ 4/8 | ▓ 4/8 | ▓ 5/8 | ▓ 4/8 | L0, L1, L2 |
| groupby_transform |   0/12 | ▒ 3/12 |   0/12 |   0/12 |   0/12 | ▓ 6/12 |   0/12 | L0, L1, L2 |
| np_roll |   0/8 |   0/8 |   0/8 |   0/8 |   0/8 |   0/8 |   0/8 | none |
| reversed_cumulative |   0/16 |   0/16 |   0/16 |   0/16 |   0/16 | ▓ 9/16 |   0/16 | L0, L1, L2 |
| argmax_param |   0/8 |   0/8 |   0/8 |   0/8 |   0/8 |   0/8 |   0/8 | none |

## Size of the leak: |Sharpe| on drift-free data, by class

Annualised, mean over the data seeds; the sign only says which way the template trades. Material: |Sharpe| of the leaky file >= 1 (largest clean twin: 0.20). Found: paired at the site by at least one linter. Events and fundamentals are independent of prices in this data, so those classes cannot show a gain here.

| Class | Median leaky | Largest leaky | Median clean | Material | Found |
|---|---|---|---|---|---|
| same_bar | 7.21 | 11.42 | 0.04 | 20/20 | 0/20 |
| negative_shift | 6.77 | 10.31 | 0.04 | 12/12 | 6/12 |
| centered_rolling | 5.66 | 19.96 | 0.06 | 8/16 | 4/8 |
| full_sample_scaling | 0.09 | 0.60 | 0.08 | 0/16 | 0/0 |
| backfill_interpolate | 0.03 | 0.03 | 0.03 | 0/16 | 0/0 |
| resample_label | 10.26 | 13.76 | 0.01 | 8/12 | 1/8 |
| asof_forward | 0.06 | 0.10 | 0.15 | 0/12 | 0/0 |
| fundamentals_period_end | 0.04 | 0.08 | 0.02 | 0/12 | 0/0 |
| restatement_overwrite | 0.10 | 0.10 | 0.02 | 0/8 | 0/0 |
| survivorship | 0.03 | 0.07 | 0.05 | 0/8 | 0/0 |
| shuffled_split | 0.10 | 0.11 | 0.06 | 0/8 | 0/0 |
| groupby_transform | 0.08 | 0.13 | 0.06 | 0/12 | 0/0 |
| np_roll | 0.08 | 0.20 | 0.08 | 0/8 | 0/0 |
| reversed_cumulative | 2.28 | 2.28 | 0.11 | 12/16 | 6/12 |
| argmax_param | 0.13 | 0.14 | 0.09 | 0/8 | 0/0 |

Material leaks found at the site, of 60:

- lookahead-lint: 3
- peekproof: 5
- backtest-audit: 4
- leakguard: 9
- overfit-gauntlet: 4
- monte-neo: 16
- nofuturedata: 5
- any linter: 17

## False positives by class (clean twins flagged / clean twins)

| Class | lookahead-lint | peekproof | backtest-audit | leakguard | overfit-gauntlet | monte-neo | nofuturedata |
|---|---|---|---|---|---|---|---|
| same_bar | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| negative_shift | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| centered_rolling | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| full_sample_scaling | 0 | 2/16 | 4/16 | 0 | 4/16 | 2/16 | 0 |
| backfill_interpolate | 1/16 | 3/16 | 0 | 1/16 | 1/16 | 3/16 | 1/16 |
| resample_label | 0 | 2/12 | 0 | 6/12 | 0 | 12/12 | 0 |
| asof_forward | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| fundamentals_period_end | 0 | 0 | 0 | 0 | 0 | 8/12 | 0 |
| restatement_overwrite | 0 | 0 | 0 | 0 | 0 | 8/8 | 0 |
| survivorship | 0 | 0 | 0 | 0 | 0 | 8/8 | 2/8 |
| shuffled_split | 3/8 | 0 | 0 | 4/8 | 4/8 | 8/8 | 1/8 |
| groupby_transform | 0 | 1/12 | 0 | 0 | 0 | 2/12 | 0 |
| np_roll | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| reversed_cumulative | 0 | 0 | 0 | 0 | 0 | 3/16 | 0 |
| argmax_param | 0 | 0 | 0 | 0 | 0 | 4/8 | 0 |

## Paired tool comparisons

Exact McNemar treats files as independent. The template sign-flip test counts each template once and is the one to read; Holm runs within each measure.

| A | B | Measure | only A | only B | McNemar p | Template p | Template p (Holm) |
|---|---|---|---|---|---|---|---|
| lookahead-lint | peekproof | recall | 3 | 29 | 2.56e-06 | 0.0356 | 0.428 |
| lookahead-lint | peekproof | paired at the site | 0 | 22 | 4.77e-07 | 0.00195 | 0.0312 |
| lookahead-lint | backtest-audit | recall | 12 | 6 | 0.238 | 0.531 | 1 |
| lookahead-lint | backtest-audit | paired at the site | 8 | 2 | 0.109 | 0.266 | 1 |
| lookahead-lint | leakguard | recall | 0 | 18 | 7.63e-06 | 0.0156 | 0.234 |
| lookahead-lint | leakguard | paired at the site | 0 | 11 | 0.000977 | 0.0156 | 0.156 |
| lookahead-lint | overfit-gauntlet | recall | 2 | 9 | 0.0654 | 0.438 | 1 |
| lookahead-lint | overfit-gauntlet | paired at the site | 2 | 4 | 0.688 | 0.875 | 1 |
| lookahead-lint | monte-neo | recall | 0 | 92 | 4.04e-28 | 4.77e-07 | 1e-05 |
| lookahead-lint | monte-neo | paired at the site | 0 | 51 | 8.88e-16 | 1.53e-05 | 0.00032 |
| lookahead-lint | nofuturedata | recall | 3 | 15 | 0.00754 | 0.141 | 1 |
| lookahead-lint | nofuturedata | paired at the site | 0 | 12 | 0.000488 | 0.0312 | 0.281 |
| peekproof | backtest-audit | recall | 38 | 6 | 9.43e-07 | 0.0247 | 0.342 |
| peekproof | backtest-audit | paired at the site | 30 | 2 | 2.46e-07 | 0.00488 | 0.0635 |
| peekproof | leakguard | recall | 27 | 19 | 0.302 | 0.636 | 1 |
| peekproof | leakguard | paired at the site | 21 | 10 | 0.0708 | 0.348 | 1 |
| peekproof | overfit-gauntlet | recall | 26 | 7 | 0.00132 | 0.123 | 1 |
| peekproof | overfit-gauntlet | paired at the site | 23 | 3 | 8.8e-05 | 0.0498 | 0.349 |
| peekproof | monte-neo | recall | 11 | 77 | 2.4e-13 | 7.63e-06 | 0.00013 |
| peekproof | monte-neo | paired at the site | 10 | 39 | 3.85e-05 | 0.00229 | 0.032 |
| peekproof | nofuturedata | recall | 28 | 14 | 0.0436 | 0.383 | 1 |
| peekproof | nofuturedata | paired at the site | 21 | 11 | 0.11 | 0.424 | 1 |
| backtest-audit | leakguard | recall | 4 | 28 | 1.93e-05 | 0.0244 | 0.342 |
| backtest-audit | leakguard | paired at the site | 0 | 17 | 1.53e-05 | 0.00195 | 0.0312 |
| backtest-audit | overfit-gauntlet | recall | 6 | 19 | 0.0146 | 0.219 | 1 |
| backtest-audit | overfit-gauntlet | paired at the site | 2 | 10 | 0.0386 | 0.188 | 1 |
| backtest-audit | monte-neo | recall | 4 | 102 | 1.27e-25 | 2.86e-06 | 5.15e-05 |
| backtest-audit | monte-neo | paired at the site | 0 | 57 | 1.39e-17 | 1.53e-05 | 0.00032 |
| backtest-audit | nofuturedata | recall | 6 | 24 | 0.00143 | 0.0732 | 0.806 |
| backtest-audit | nofuturedata | paired at the site | 2 | 20 | 0.000121 | 0.00928 | 0.102 |
| leakguard | overfit-gauntlet | recall | 15 | 4 | 0.0192 | 0.195 | 1 |
| leakguard | overfit-gauntlet | paired at the site | 9 | 0 | 0.00391 | 0.00781 | 0.0938 |
| leakguard | monte-neo | recall | 0 | 74 | 1.06e-22 | 7.63e-06 | 0.00013 |
| leakguard | monte-neo | paired at the site | 2 | 42 | 1.13e-10 | 0.00058 | 0.0104 |
| leakguard | nofuturedata | recall | 14 | 8 | 0.286 | 0.559 | 1 |
| leakguard | nofuturedata | paired at the site | 5 | 6 | 1 | 1 | 1 |
| overfit-gauntlet | monte-neo | recall | 0 | 85 | 5.17e-26 | 9.54e-07 | 1.91e-05 |
| overfit-gauntlet | monte-neo | paired at the site | 0 | 49 | 3.55e-15 | 3.05e-05 | 0.00058 |
| overfit-gauntlet | nofuturedata | recall | 7 | 12 | 0.359 | 0.625 | 1 |
| overfit-gauntlet | nofuturedata | paired at the site | 0 | 10 | 0.00195 | 0.0312 | 0.281 |
| monte-neo | nofuturedata | recall | 80 | 0 | 1.65e-24 | 1.91e-06 | 3.62e-05 |
| monte-neo | nofuturedata | paired at the site | 41 | 2 | 2.15e-10 | 0.000732 | 0.0125 |

## Coverage

Classes no linter finds at the site at any level: same_bar, np_roll, argmax_param.

## False positives (clean twins flagged, file:line rule)

- lookahead-lint: `files/f834a51612c.py:10` LA002 (backfill_interpolate, L3, pandas)
- lookahead-lint: `files/fb41b7c1d50.py:7` LA005 (shuffled_split, L2, pandas)
- lookahead-lint: `files/fc038e732d2.py:14` LA005 (shuffled_split, L1, pandas)
- lookahead-lint: `files/fdeca3fe8b9.py:11` LA005 (shuffled_split, L3, pandas)
- peekproof: `files/f0deee7ef84.py:10` PP006 (full_sample_scaling, L3, polars)
- peekproof: `files/f3048cb9278.py:10` PP002 (backfill_interpolate, L3, polars)
- peekproof: `files/f38c7724613.py:10` PP002 (backfill_interpolate, L3, pandas)
- peekproof: `files/f6cbb464092.py:10` PP006 (groupby_transform, L3, polars)
- peekproof: `files/f834a51612c.py:10` PP002 (backfill_interpolate, L3, pandas)
- peekproof: `files/fafa8afaf8e.py:15` PP011 (resample_label, L3, pandas)
- peekproof: `files/fb08522df12.py:16` PP011 (resample_label, L3, polars)
- peekproof: `files/fd6abfb0dd4.py:8` PP006 (full_sample_scaling, L3, pandas)
- backtest-audit: `files/f3611a38879.py:6` LEAK001 (full_sample_scaling, L2, numpy)
- backtest-audit: `files/f53d2a3bb73.py:11` LEAK001 (full_sample_scaling, L0, numpy)
- backtest-audit: `files/f9e5cc45462.py:12` LEAK001 (full_sample_scaling, L1, numpy)
- backtest-audit: `files/ff50e3b09f6.py:10` LEAK001 (full_sample_scaling, L3, numpy)
- leakguard: `files/f57a08418fa.py:9` LG009 (resample_label, L3, pandas)
- leakguard: `files/f7080e83daa.py:5` LG009 (resample_label, L2, pandas)
- leakguard: `files/f834a51612c.py:10` LG007 (backfill_interpolate, L3, pandas)
- leakguard: `files/f8f7fb33684.py:7` LG009 (resample_label, L1, pandas)
- leakguard: `files/fafa8afaf8e.py:9` LG009 (resample_label, L3, pandas)
- leakguard: `files/fb41b7c1d50.py:7` LG004 (shuffled_split, L2, pandas)
- leakguard: `files/fc038e732d2.py:14` LG004 (shuffled_split, L1, pandas)
- leakguard: `files/fc394eaf260.py:11` LG004 (shuffled_split, L3, numpy)
- leakguard: `files/fcd5403ef8e.py:9` LG009 (resample_label, L1, pandas)
- leakguard: `files/fdeca3fe8b9.py:11` LG004 (shuffled_split, L3, pandas)
- leakguard: `files/ffc686b6a44.py:5` LG009 (resample_label, L2, pandas)
- overfit-gauntlet: `files/f0c0fe48761.py:5` LA07 (full_sample_scaling, L0, pandas)
- overfit-gauntlet: `files/f482020a751.py:6` LA07 (full_sample_scaling, L1, pandas)
- overfit-gauntlet: `files/f834a51612c.py:10` LA03 (backfill_interpolate, L3, pandas)
- overfit-gauntlet: `files/f8b919bab7f.py:2` LA07 (full_sample_scaling, L2, pandas)
- overfit-gauntlet: `files/fb41b7c1d50.py:7` LA04 (shuffled_split, L2, pandas)
- overfit-gauntlet: `files/fc038e732d2.py:14` LA04 (shuffled_split, L1, pandas)
- overfit-gauntlet: `files/fc394eaf260.py:11` LA05 (shuffled_split, L3, numpy)
- overfit-gauntlet: `files/fd6abfb0dd4.py:8` LA07 (full_sample_scaling, L3, pandas)
- overfit-gauntlet: `files/fd6abfb0dd4.py:10` LA07 (full_sample_scaling, L3, pandas)
- overfit-gauntlet: `files/fdeca3fe8b9.py:11` LA04 (shuffled_split, L3, pandas)
- monte-neo: `files/f0a92ffa630.py:14` full_sample_rank (restatement_overwrite, L2, pandas)
- monte-neo: `files/f0cef94e89e.py:8` full_sample_rank (fundamentals_period_end, L1, pandas)
- monte-neo: `files/f0f7afb1e23.py:9` full_sample_rank (survivorship, L2, pandas)
- monte-neo: `files/f16ebc8abc7.py:17` full_sample_rank (fundamentals_period_end, L3, pandas)
- monte-neo: `files/f2f2cf488ee.py:9` full_sample_rank (survivorship, L2, pandas)
- monte-neo: `files/f3048cb9278.py:10` interpolate (backfill_interpolate, L3, polars)
- monte-neo: `files/f38c7724613.py:10` interpolate (backfill_interpolate, L3, pandas)
- monte-neo: `files/f38fc7519d2.py:10` full_sample_stat (full_sample_scaling, L3, numpy)
- monte-neo: `files/f421a055910.py:12` full_sample_rank (fundamentals_period_end, L2, pandas)
- monte-neo: `files/f4660f30430.py:8` group_aggregate (resample_label, L0, pandas)
- monte-neo: `files/f4660f30430.py:8` htf_without_shift (resample_label, L0, pandas)
- monte-neo: `files/f4c5ee86c7c.py:4` full_sample_rank (survivorship, L0, pandas)
- monte-neo: `files/f501f384ce3.py:13` full_sample_rank (fundamentals_period_end, L0, pandas)
- monte-neo: `files/f54bbd0f076.py:24` full_sample_stat (argmax_param, L2, numpy)
- monte-neo: `files/f54bbd0f076.py:25` full_sample_stat (argmax_param, L2, numpy)
- monte-neo: `files/f56ecb9ccc5.py:4` full_sample_rank (survivorship, L0, pandas)
- monte-neo: `files/f57a08418fa.py:9` group_aggregate (resample_label, L3, pandas)
- monte-neo: `files/f57a08418fa.py:9` htf_without_shift (resample_label, L3, pandas)
- monte-neo: `files/f59f6782126.py:5` full_sample_stat (resample_label, L2, polars)
- monte-neo: `files/f64413aecd7.py:2` group_aggregate (restatement_overwrite, L2, pandas)
- monte-neo: `files/f64413aecd7.py:13` full_sample_rank (restatement_overwrite, L2, pandas)
- monte-neo: `files/f6c9047a54d.py:6` group_aggregate (resample_label, L0, pandas)
- monte-neo: `files/f6c9047a54d.py:6` htf_without_shift (resample_label, L0, pandas)
- monte-neo: `files/f6ea5f2c177.py:16` full_sample_stat (shuffled_split, L2, numpy)
- monte-neo: `files/f6fc75ea843.py:10` reversed_cumulative (reversed_cumulative, L3, pandas)
- monte-neo: `files/f7080e83daa.py:5` group_aggregate (resample_label, L2, pandas)
- monte-neo: `files/f7080e83daa.py:5` htf_without_shift (resample_label, L2, pandas)
- monte-neo: `files/f76506912f8.py:11` full_sample_stat (shuffled_split, L0, numpy)
- monte-neo: `files/f7c8ac42334.py:8` reversed_cumulative (reversed_cumulative, L3, pandas)
- monte-neo: `files/f833c58245f.py:10` reversed_cumulative (reversed_cumulative, L3, numpy)
- monte-neo: `files/f834a51612c.py:10` backward_fill (backfill_interpolate, L3, pandas)
- monte-neo: `files/f83c60b1273.py:7` group_aggregate (restatement_overwrite, L3, pandas)
- monte-neo: `files/f83c60b1273.py:18` full_sample_rank (restatement_overwrite, L3, pandas)
- monte-neo: `files/f8600f5c567.py:19` full_sample_stat (argmax_param, L0, numpy)
- monte-neo: `files/f8600f5c567.py:20` full_sample_stat (argmax_param, L0, numpy)
- monte-neo: `files/f88c32ce1aa.py:9` full_sample_rank (restatement_overwrite, L0, pandas)
- monte-neo: `files/f8996984ecb.py:8` group_aggregate (groupby_transform, L3, pandas)
- monte-neo: `files/f8f7fb33684.py:7` group_aggregate (resample_label, L1, pandas)
- monte-neo: `files/f8f7fb33684.py:7` htf_without_shift (resample_label, L1, pandas)
- monte-neo: `files/f933abdd2d6.py:7` full_sample_stat (resample_label, L0, polars)
- monte-neo: `files/f962b496ded.py:10` full_sample_rank (restatement_overwrite, L1, pandas)
- monte-neo: `files/fa4e1143d65.py:4` full_sample_rank (survivorship, L1, pandas)
- monte-neo: `files/fa5c3744bfd.py:9` full_sample_stat (shuffled_split, L0, pandas)
- monte-neo: `files/fafa8afaf8e.py:9` group_aggregate (resample_label, L3, pandas)
- monte-neo: `files/fafa8afaf8e.py:9` htf_without_shift (resample_label, L3, pandas)
- monte-neo: `files/fb02262451d.py:8` last_row (survivorship, L3, pandas)
- monte-neo: `files/fb02262451d.py:17` full_sample_rank (survivorship, L3, pandas)
- monte-neo: `files/fb08522df12.py:9` full_sample_stat (resample_label, L3, polars)
- monte-neo: `files/fb41b7c1d50.py:7` shuffled_split (shuffled_split, L2, pandas)
- monte-neo: `files/fb41b7c1d50.py:14` full_sample_stat (shuffled_split, L2, pandas)
- monte-neo: `files/fb8c73e0d02.py:14` full_sample_rank (fundamentals_period_end, L1, pandas)
- monte-neo: `files/fbb8c9c4012.py:8` group_aggregate (groupby_transform, L3, pandas)
- monte-neo: `files/fbef64113a6.py:28` full_sample_stat (argmax_param, L3, numpy)
- monte-neo: `files/fbef64113a6.py:29` full_sample_stat (argmax_param, L3, numpy)
- monte-neo: `files/fc038e732d2.py:9` full_sample_stat (shuffled_split, L1, pandas)
- monte-neo: `files/fc3088c45f2.py:8` full_sample_stat (resample_label, L1, polars)
- monte-neo: `files/fc35b6777ab.py:4` group_aggregate (restatement_overwrite, L0, pandas)
- monte-neo: `files/fc35b6777ab.py:8` full_sample_rank (restatement_overwrite, L0, pandas)
- monte-neo: `files/fc35cc6aee1.py:4` full_sample_rank (survivorship, L1, pandas)
- monte-neo: `files/fc394eaf260.py:11` kfold_split (shuffled_split, L3, numpy)
- monte-neo: `files/fc394eaf260.py:23` full_sample_stat (shuffled_split, L3, numpy)
- monte-neo: `files/fc411cf824a.py:18` full_sample_rank (fundamentals_period_end, L2, pandas)
- monte-neo: `files/fc890317eb6.py:8` last_row (survivorship, L3, pandas)
- monte-neo: `files/fc890317eb6.py:17` full_sample_rank (survivorship, L3, pandas)
- monte-neo: `files/fcd5403ef8e.py:9` group_aggregate (resample_label, L1, pandas)
- monte-neo: `files/fcd5403ef8e.py:9` htf_without_shift (resample_label, L1, pandas)
- monte-neo: `files/fce3e42aa27.py:22` full_sample_rank (fundamentals_period_end, L3, pandas)
- monte-neo: `files/fd6abfb0dd4.py:8` full_sample_stat (full_sample_scaling, L3, pandas)
- monte-neo: `files/fdaada941ea.py:20` full_sample_stat (argmax_param, L1, numpy)
- monte-neo: `files/fdaada941ea.py:21` full_sample_stat (argmax_param, L1, numpy)
- monte-neo: `files/fdeca3fe8b9.py:11` shuffled_split (shuffled_split, L3, pandas)
- monte-neo: `files/fdeca3fe8b9.py:18` full_sample_stat (shuffled_split, L3, pandas)
- monte-neo: `files/fe9a64747e9.py:11` full_sample_stat (shuffled_split, L1, numpy)
- monte-neo: `files/fead63e01a0.py:19` full_sample_rank (restatement_overwrite, L3, pandas)
- monte-neo: `files/feb4a43ac2f.py:5` group_aggregate (restatement_overwrite, L1, pandas)
- monte-neo: `files/feb4a43ac2f.py:9` full_sample_rank (restatement_overwrite, L1, pandas)
- monte-neo: `files/ff32d5fbc7d.py:7` full_sample_rank (fundamentals_period_end, L0, pandas)
- monte-neo: `files/ffc686b6a44.py:5` group_aggregate (resample_label, L2, pandas)
- monte-neo: `files/ffc686b6a44.py:5` htf_without_shift (resample_label, L2, pandas)
- nofuturedata: `files/f834a51612c.py:10` SRC002 (backfill_interpolate, L3, pandas)
- nofuturedata: `files/fb02262451d.py:8` SRC009 (survivorship, L3, pandas)
- nofuturedata: `files/fc394eaf260.py:11` SRC011 (shuffled_split, L3, numpy)
- nofuturedata: `files/fc890317eb6.py:8` SRC009 (survivorship, L3, pandas)

## Leaky L0 files no linter finds at the site (file:site lines)

- `files/f44e07a3bc0.py:7` (same_bar, pandas)
- `files/f4e28185ec3.py:13` (argmax_param, pandas)
- `files/f4e6f6a45b3.py:8` (same_bar, pandas)
- `files/f5f728c36be.py:12` (same_bar, numpy)
- `files/f5fcc6cca2e.py:8` (same_bar, polars)
- `files/f638521e2b0.py:4` (restatement_overwrite, pandas)
- `files/f84989b112f.py:4` (fundamentals_period_end, pandas)
- `files/f8c08f5f686.py:11` (full_sample_scaling, numpy)
- `files/f9c6f56409b.py:7` (reversed_cumulative, polars)
- `files/fa29e3ce624.py:12` (argmax_param, numpy)
- `files/fac4dcef468.py:9` (np_roll, numpy)
- `files/fd8a85e7592.py:7` (resample_label, polars)
- `files/fe4d5ed6db5.py:8,9,10` (np_roll, numpy)
- `files/ff9956ddc5d.py:12` (same_bar, numpy)
