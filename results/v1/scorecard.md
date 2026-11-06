# Scorecard (corpus seed 20261030)

Corpus: 368 files = 184 leak/clean pairs, 15 classes, 30 templates. Oracle: 368/368 labels confirmed (9873 script runs, n = 5000 rows, 16 cut points x 3 perturbation modes).
Intervals: pooled rates use a cluster bootstrap over templates (10000 resamples, percentile 95%); per-cell rates use Clopper-Pearson 95%.

## Headline (each tool's documented leakage rules)

| Tool | Version | Recall | False-positive rate | Paired discrimination | Paired at the site |
|---|---|---|---|---|---|
| lookahead-lint | 1.0.1 | 7.6% [2.3, 14.7] (14/184) | 2.2% [0.0, 6.2] (4/184) | 5.4% [1.8, 9.8] (10/184) | 5.4% [1.8, 9.8] (10/184) |
| peekproof | 0.1.0+e6c56c3 | 21.2% [10.6, 32.7] (39/184) | 3.8% [1.1, 6.9] (7/184) | 17.4% [9.1, 26.1] (32/184) | 17.4% [9.1, 26.1] (32/184) |
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
| peekproof | 18.5% | 15.3% |
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
| peekproof | 39/39 | 39/39 | 58% |
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
| peekproof | 21.2% [10.6, 32.7] (39/184) | 3.8% [1.1, 6.9] (7/184) | 17.4% [9.1, 26.1] (32/184) |
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
| peekproof | 43.5% [28.9, 58.9] (20/46) | 13.0% [4.9, 26.3] (6/46) | 13.0% [4.9, 26.3] (6/46) | 15.2% [6.3, 28.9] (7/46) |
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
| peekproof | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) | 0.0% [0.0, 7.7] (0/46) | 15.2% [6.3, 28.9] (7/46) |
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
| peekproof | 20.0% [12.7, 29.2] (20/100) | 0.0% [0.0, 9.7] (0/36) | 39.6% [25.8, 54.7] (19/48) |
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
| resample_label |   0/12 | ░ 1/12 |   0/12 | ▓ 8/12 |   0/12 | █ 12/12 | ░ 2/12 |
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
| same_bar | 7.21 | 16.29 | 0.03 | 20/20 | 0/20 |
| negative_shift | 6.75 | 9.54 | 0.03 | 12/12 | 6/12 |
| centered_rolling | 6.43 | 19.96 | 0.06 | 9/16 | 5/9 |
| full_sample_scaling | 0.09 | 0.60 | 0.08 | 0/16 | 0/0 |
| backfill_interpolate | 0.03 | 0.03 | 0.03 | 0/16 | 0/0 |
| resample_label | 10.26 | 13.76 | 0.01 | 8/12 | 1/8 |
| asof_forward | 0.06 | 0.10 | 0.15 | 0/12 | 0/0 |
| fundamentals_period_end | 0.04 | 0.08 | 0.02 | 0/12 | 0/0 |
| restatement_overwrite | 0.10 | 0.10 | 0.02 | 0/8 | 0/0 |
| survivorship | 0.06 | 0.14 | 0.03 | 0/8 | 0/0 |
| shuffled_split | 0.10 | 0.11 | 0.06 | 0/8 | 0/0 |
| groupby_transform | 0.08 | 0.13 | 0.05 | 0/12 | 0/0 |
| np_roll | 0.08 | 0.20 | 0.08 | 0/8 | 0/0 |
| reversed_cumulative | 2.28 | 2.28 | 0.11 | 12/16 | 6/12 |
| argmax_param | 0.11 | 0.14 | 0.10 | 0/8 | 0/0 |

Material leaks found at the site, of 61:

- lookahead-lint: 4
- peekproof: 6
- backtest-audit: 4
- leakguard: 10
- overfit-gauntlet: 5
- monte-neo: 17
- nofuturedata: 6
- any linter: 18

## False positives by class (clean twins flagged / clean twins)

| Class | lookahead-lint | peekproof | backtest-audit | leakguard | overfit-gauntlet | monte-neo | nofuturedata |
|---|---|---|---|---|---|---|---|
| same_bar | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| negative_shift | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| centered_rolling | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| full_sample_scaling | 0 | 2/16 | 4/16 | 0 | 4/16 | 2/16 | 0 |
| backfill_interpolate | 1/16 | 3/16 | 0 | 1/16 | 1/16 | 3/16 | 1/16 |
| resample_label | 0 | 1/12 | 0 | 6/12 | 0 | 12/12 | 0 |
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
| lookahead-lint | peekproof | recall | 3 | 28 | 4.65e-06 | 0.0459 | 0.551 |
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
| peekproof | backtest-audit | recall | 37 | 6 | 1.64e-06 | 0.0297 | 0.386 |
| peekproof | backtest-audit | paired at the site | 30 | 2 | 2.46e-07 | 0.00488 | 0.0635 |
| peekproof | leakguard | recall | 27 | 20 | 0.382 | 0.688 | 1 |
| peekproof | leakguard | paired at the site | 21 | 10 | 0.0708 | 0.348 | 1 |
| peekproof | overfit-gauntlet | recall | 25 | 7 | 0.0021 | 0.145 | 1 |
| peekproof | overfit-gauntlet | paired at the site | 23 | 3 | 8.8e-05 | 0.0498 | 0.349 |
| peekproof | monte-neo | recall | 11 | 78 | 1.37e-13 | 7.63e-06 | 0.00013 |
| peekproof | monte-neo | paired at the site | 10 | 39 | 3.85e-05 | 0.00229 | 0.032 |
| peekproof | nofuturedata | recall | 27 | 14 | 0.0596 | 0.414 | 1 |
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
- overfit-gauntlet: `files/f032dfffef6.py:11` LA05 (shuffled_split, L3, numpy)
- overfit-gauntlet: `files/f421ec9900a.py:10` LA03 (backfill_interpolate, L3, pandas)
- overfit-gauntlet: `files/f518d028dc7.py:11` LA04 (shuffled_split, L3, pandas)
- overfit-gauntlet: `files/f646bb135d7.py:7` LA04 (shuffled_split, L2, pandas)
- overfit-gauntlet: `files/f737812dbdf.py:2` LA07 (full_sample_scaling, L2, pandas)
- overfit-gauntlet: `files/f7e63712502.py:8` LA07 (full_sample_scaling, L3, pandas)
- overfit-gauntlet: `files/f7e63712502.py:10` LA07 (full_sample_scaling, L3, pandas)
- overfit-gauntlet: `files/fa0628b0c66.py:5` LA07 (full_sample_scaling, L0, pandas)
- overfit-gauntlet: `files/fcd1b3331e2.py:14` LA04 (shuffled_split, L1, pandas)
- overfit-gauntlet: `files/ffaedf0b35d.py:6` LA07 (full_sample_scaling, L1, pandas)
- monte-neo: `files/f006bd798a4.py:8` last_row (survivorship, L3, pandas)
- monte-neo: `files/f006bd798a4.py:17` full_sample_rank (survivorship, L3, pandas)
- monte-neo: `files/f032dfffef6.py:11` kfold_split (shuffled_split, L3, numpy)
- monte-neo: `files/f032dfffef6.py:23` full_sample_stat (shuffled_split, L3, numpy)
- monte-neo: `files/f058a6adc75.py:10` interpolate (backfill_interpolate, L3, polars)
- monte-neo: `files/f09a692b7e3.py:6` group_aggregate (resample_label, L0, pandas)
- monte-neo: `files/f09a692b7e3.py:6` htf_without_shift (resample_label, L0, pandas)
- monte-neo: `files/f10293280c7.py:17` full_sample_rank (fundamentals_period_end, L3, pandas)
- monte-neo: `files/f13d184f145.py:22` full_sample_rank (fundamentals_period_end, L3, pandas)
- monte-neo: `files/f1ae6c81230.py:10` interpolate (backfill_interpolate, L3, pandas)
- monte-neo: `files/f1cada33e73.py:19` full_sample_rank (restatement_overwrite, L3, pandas)
- monte-neo: `files/f1d92a9eaf7.py:4` full_sample_rank (survivorship, L1, pandas)
- monte-neo: `files/f22f084523f.py:9` group_aggregate (resample_label, L3, pandas)
- monte-neo: `files/f22f084523f.py:9` htf_without_shift (resample_label, L3, pandas)
- monte-neo: `files/f25b1f7dd5a.py:4` group_aggregate (restatement_overwrite, L0, pandas)
- monte-neo: `files/f25b1f7dd5a.py:8` full_sample_rank (restatement_overwrite, L0, pandas)
- monte-neo: `files/f272105f636.py:7` full_sample_rank (fundamentals_period_end, L0, pandas)
- monte-neo: `files/f2b3bc007ee.py:11` full_sample_stat (shuffled_split, L0, numpy)
- monte-neo: `files/f32bf59a9ab.py:14` full_sample_rank (restatement_overwrite, L2, pandas)
- monte-neo: `files/f35c3f57c0a.py:18` full_sample_rank (fundamentals_period_end, L2, pandas)
- monte-neo: `files/f3c3c9cf9de.py:5` group_aggregate (resample_label, L2, pandas)
- monte-neo: `files/f3c3c9cf9de.py:5` htf_without_shift (resample_label, L2, pandas)
- monte-neo: `files/f421ec9900a.py:10` backward_fill (backfill_interpolate, L3, pandas)
- monte-neo: `files/f4da5e44a18.py:9` group_aggregate (resample_label, L1, pandas)
- monte-neo: `files/f4da5e44a18.py:9` htf_without_shift (resample_label, L1, pandas)
- monte-neo: `files/f4f47a1d743.py:9` full_sample_rank (survivorship, L2, pandas)
- monte-neo: `files/f518d028dc7.py:11` shuffled_split (shuffled_split, L3, pandas)
- monte-neo: `files/f518d028dc7.py:18` full_sample_stat (shuffled_split, L3, pandas)
- monte-neo: `files/f559580cbf0.py:10` reversed_cumulative (reversed_cumulative, L3, pandas)
- monte-neo: `files/f566d93c71a.py:9` full_sample_rank (restatement_overwrite, L0, pandas)
- monte-neo: `files/f576a6b8051.py:8` group_aggregate (groupby_transform, L3, pandas)
- monte-neo: `files/f57e37364d1.py:9` full_sample_rank (survivorship, L2, pandas)
- monte-neo: `files/f590c674eed.py:7` full_sample_stat (resample_label, L0, polars)
- monte-neo: `files/f5d5bbfc060.py:8` group_aggregate (groupby_transform, L3, pandas)
- monte-neo: `files/f5f5746dd0e.py:8` full_sample_rank (fundamentals_period_end, L1, pandas)
- monte-neo: `files/f646bb135d7.py:7` shuffled_split (shuffled_split, L2, pandas)
- monte-neo: `files/f646bb135d7.py:14` full_sample_stat (shuffled_split, L2, pandas)
- monte-neo: `files/f6533b240b9.py:5` group_aggregate (resample_label, L2, pandas)
- monte-neo: `files/f6533b240b9.py:5` htf_without_shift (resample_label, L2, pandas)
- monte-neo: `files/f67b8a95d75.py:12` full_sample_rank (fundamentals_period_end, L2, pandas)
- monte-neo: `files/f6a6471752b.py:7` group_aggregate (restatement_overwrite, L3, pandas)
- monte-neo: `files/f6a6471752b.py:18` full_sample_rank (restatement_overwrite, L3, pandas)
- monte-neo: `files/f6b137991dc.py:5` full_sample_stat (resample_label, L2, polars)
- monte-neo: `files/f6daf5fdc48.py:8` last_row (survivorship, L3, pandas)
- monte-neo: `files/f6daf5fdc48.py:17` full_sample_rank (survivorship, L3, pandas)
- monte-neo: `files/f70162bda20.py:9` full_sample_stat (shuffled_split, L0, pandas)
- monte-neo: `files/f705c4d79ca.py:8` full_sample_stat (resample_label, L1, polars)
- monte-neo: `files/f7773860df9.py:20` full_sample_stat (argmax_param, L1, numpy)
- monte-neo: `files/f7773860df9.py:21` full_sample_stat (argmax_param, L1, numpy)
- monte-neo: `files/f7bfb92cba0.py:4` full_sample_rank (survivorship, L1, pandas)
- monte-neo: `files/f7e63712502.py:8` full_sample_stat (full_sample_scaling, L3, pandas)
- monte-neo: `files/f89193c4021.py:10` reversed_cumulative (reversed_cumulative, L3, numpy)
- monte-neo: `files/f927feb9c7f.py:13` full_sample_rank (fundamentals_period_end, L0, pandas)
- monte-neo: `files/f958ff4b265.py:11` full_sample_stat (shuffled_split, L1, numpy)
- monte-neo: `files/f998f6b2dd5.py:14` full_sample_rank (fundamentals_period_end, L1, pandas)
- monte-neo: `files/fa4ba8a838d.py:19` full_sample_stat (argmax_param, L0, numpy)
- monte-neo: `files/fa4ba8a838d.py:20` full_sample_stat (argmax_param, L0, numpy)
- monte-neo: `files/fb78bd05c96.py:10` full_sample_stat (full_sample_scaling, L3, numpy)
- monte-neo: `files/fb9ed7cb35b.py:4` full_sample_rank (survivorship, L0, pandas)
- monte-neo: `files/fbaa8a4f35d.py:9` group_aggregate (resample_label, L3, pandas)
- monte-neo: `files/fbaa8a4f35d.py:9` htf_without_shift (resample_label, L3, pandas)
- monte-neo: `files/fbbd2ae3178.py:28` full_sample_stat (argmax_param, L3, numpy)
- monte-neo: `files/fbbd2ae3178.py:29` full_sample_stat (argmax_param, L3, numpy)
- monte-neo: `files/fbc3d5df147.py:8` group_aggregate (resample_label, L0, pandas)
- monte-neo: `files/fbc3d5df147.py:8` htf_without_shift (resample_label, L0, pandas)
- monte-neo: `files/fc90b41a756.py:8` reversed_cumulative (reversed_cumulative, L3, pandas)
- monte-neo: `files/fcc397d5ded.py:2` group_aggregate (restatement_overwrite, L2, pandas)
- monte-neo: `files/fcc397d5ded.py:13` full_sample_rank (restatement_overwrite, L2, pandas)
- monte-neo: `files/fcd1b3331e2.py:9` full_sample_stat (shuffled_split, L1, pandas)
- monte-neo: `files/fce33998f64.py:7` group_aggregate (resample_label, L1, pandas)
- monte-neo: `files/fce33998f64.py:7` htf_without_shift (resample_label, L1, pandas)
- monte-neo: `files/fd2a303b52e.py:4` full_sample_rank (survivorship, L0, pandas)
- monte-neo: `files/fd685203cc2.py:24` full_sample_stat (argmax_param, L2, numpy)
- monte-neo: `files/fd685203cc2.py:25` full_sample_stat (argmax_param, L2, numpy)
- monte-neo: `files/fd7916f7039.py:16` full_sample_stat (shuffled_split, L2, numpy)
- monte-neo: `files/feaf443153a.py:9` full_sample_stat (resample_label, L3, polars)
- monte-neo: `files/ff0036774b9.py:5` group_aggregate (restatement_overwrite, L1, pandas)
- monte-neo: `files/ff0036774b9.py:9` full_sample_rank (restatement_overwrite, L1, pandas)
- monte-neo: `files/ffe0fd79af9.py:10` full_sample_rank (restatement_overwrite, L1, pandas)
- nofuturedata: `files/f006bd798a4.py:8` SRC009 (survivorship, L3, pandas)
- nofuturedata: `files/f032dfffef6.py:11` SRC011 (shuffled_split, L3, numpy)
- nofuturedata: `files/f421ec9900a.py:10` SRC002 (backfill_interpolate, L3, pandas)
- nofuturedata: `files/f6daf5fdc48.py:8` SRC009 (survivorship, L3, pandas)

## Leaky L0 files no linter finds at the site (file:site lines)

- `files/f0494aafcfb.py:12` (same_bar, numpy)
- `files/f07bd3722e6.py:8,9,10` (np_roll, numpy)
- `files/f12808039d4.py:4` (fundamentals_period_end, pandas)
- `files/f178169036d.py:12` (argmax_param, numpy)
- `files/f18085e9e7b.py:12` (same_bar, numpy)
- `files/f1b85716c54.py:11` (full_sample_scaling, numpy)
- `files/f1d832b7418.py:9` (np_roll, numpy)
- `files/f221fd1c552.py:7` (same_bar, pandas)
- `files/f416142bd2a.py:7` (resample_label, polars)
- `files/f4435c06ba7.py:13` (argmax_param, pandas)
- `files/f463f8bb8aa.py:4` (restatement_overwrite, pandas)
- `files/f87b0f00ff6.py:8` (same_bar, polars)
- `files/fd5996b1360.py:8` (same_bar, pandas)
- `files/fd6baad3d7c.py:7` (reversed_cumulative, polars)
