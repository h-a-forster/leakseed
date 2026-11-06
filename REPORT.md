# leakseed report: seven static linters on 184 seeded look-ahead leaks

Corpus v1, results as of 2026-11-06. All numbers come from `results/v1/scorecard.md` or the files
next to it (`probes.md`, `oracle.jsonl`, `oracle_replication.json`, `findings/`) and from
`results/fresh/`. Rates are of 184 leaky files or pairs unless stated, and intervals are 95%.
Estimands, oracle and statistics: [docs/DESIGN.md](docs/DESIGN.md).

## Summary

- **The best linter finds a third of the leaks at the site.** monte-neo 0.54.0 scores 33.2%
  [22.9, 43.4] (61/184) paired at the site: a flag on the leak and none at the same place in the
  clean twin. Counting a pair that at least one tool scores on its own gives 39.7% [28.6, 50.5]
  (73/184).
- **The leaks that pay are mostly missed.** 61 leaky files reach |Sharpe| >= 1 on drift-free data,
  against 0.19 for the largest clean twin. No tool finds 43 of those 61 at the site.
- **Three classes are unfound at every level:** `same_bar` (0/20, and all 20 are material),
  `np_roll` and `argmax_param`. The same holds on both fresh generator seeds.
- **File-level recall flatters.** monte-neo's recall is 57.6%, but its false-positive rate is 31.5%,
  because many flags land on code both twins share. At its `fail` severity alone it scores 23.4%
  at the site with 4.3% false positives.
- **One local variable defeats most tools.** Four of seven lose more than half their site score
  from L0 to L1. monte-neo inlines constants and stays at 24/46.

## Data

368 scripts = 184 leak/clean pairs: 15 classes x 4 obfuscation levels x pandas/numpy/polars, from
30 templates. The twins of a pair differ only by the minimal fix.

The oracle replaces everything observed after a cut t and checks whether the positions held up to
t + 1 move. It confirms 368/368 labels on data seeds 2026, 7, 11 and 13, and on fresh generator
seeds 101 and 202. On the default data it used 9,873 script runs, and the 184 leak witnesses are
180 from the values mode and 4 from availability. A leak label is a proof, because the witness is
a concrete pair of histories. A clean label is evidence.

## Scorecard

Each tool's documented leakage rules at any severity. Intervals are a cluster bootstrap over the
30 templates.

| Tool | Paired at the site | Recall | False-positive rate |
|---|---|---|---|
| monte-neo 0.54.0 | 33.2% [22.9, 43.4] (61) | 57.6% (106) | 31.5% (58) |
| peekproof e6c56c3 | 17.4% [9.1, 26.1] (32) | 21.2% (39) | 3.8% (7) |
| nofuturedata fb46880 | 12.0% [6.1, 19.2] (22) | 14.1% (26) | 2.2% (4) |
| leakguard 0.1.1 | 11.4% [5.5, 18.2] (21) | 17.4% (32) | 6.0% (11) |
| overfit-gauntlet 0.1.0 | 6.5% [2.1, 12.0] (12) | 11.4% (21) | 4.9% (9) |
| lookahead-lint 1.0.1 | 5.4% [1.8, 9.8] (10) | 7.6% (14) | 2.2% (4) |
| backtest-audit 1.0.0 | 2.2% [0.0, 7.0] (4) | 4.3% (8) | 2.2% (4) |
| ruff defaults (null) | 0.0% (0) | 0.0% (0) | 0.0% (0) |
| any linter | 39.7% [28.6, 50.5] (73) | 65.8% (121) | 36.4% (67) |

The any-linter row counts a case that at least one tool scores on its own, so it is not the result
of running all seven as one tool. Joining the seven tools' flags in `findings/` gives 67/184 at the
site and 54/184 paired discrimination, against 73 and 70 in the row: one tool's flag on a clean twin
cancels another tool's hit.

Top severity only (recall / false positives / site): monte-neo 27.7 / 4.3 / 23.4, leakguard
13.0 / 2.7 / 10.3, peekproof 8.7 / 0.5 / 8.2, overfit-gauntlet 7.1 / 2.2 / 4.9. Mean over classes
at the site: monte-neo 33.1%, peekproof 15.3%, nofuturedata 14.3%.

## Tool comparisons

At the site, 16 of 21 pairs pass p < 0.05 with McNemar over files, which treats files as
independent. Only 8 of 21 survive the template sign-flip test with Holm:

- monte-neo beats backtest-audit (0.0003), lookahead-lint (0.0003), overfit-gauntlet (0.0006),
  leakguard (0.010), nofuturedata (0.013) and peekproof (0.032).
- peekproof beats lookahead-lint (0.031).
- leakguard beats backtest-audit (0.031).

peekproof against backtest-audit shows the gap: McNemar 2.5e-07, template test 0.064. For recall
the counts are 15 and 6.

## By obfuscation level

Paired at the site, of 46 at each level:

| Tool | L0 | L1 | L2 | L3 |
|---|---|---|---|---|
| monte-neo | 24 | 24 | 13 | 0 |
| peekproof | 20 | 6 | 6 | 0 |
| nofuturedata | 14 | 4 | 4 | 0 |
| leakguard | 12 | 7 | 2 | 0 |
| overfit-gauntlet | 8 | 2 | 2 | 0 |
| lookahead-lint | 8 | 1 | 1 | 0 |
| backtest-audit | 2 | 2 | 0 | 0 |

No tool finds 14 L0 leaks, the plainest form. L3 is 0 by design, because both twins hold the leaky
expression and only a config string differs. Flagging that dead branch costs false positives at L3
(monte-neo 22/46, peekproof 7/46).

## Coverage

`same_bar`, `np_roll` and `argmax_param` are unfound at the site at any level. The probes
(`results/v1/probes.md`) show these are gaps in form, not in intent:

- PP010 fires once an explicit `signal * returns` line exists.
- PP001, negative_roll and SRC012 catch a negative `np.roll`.
- PP004/PP005, LG004, full_sample_fit and SRC011 catch a time-blind `GridSearchCV`.

Left unflagged in the corpus: a position held with no lag, a positive wrapping roll and a
loop-based parameter search. `restatement_overwrite` is found only by monte-neo, in 2 of 8 pairs.

## Size of the leak

|Sharpe| of holding the positions on drift-free data, five data seeds. Material means at least 1.

| Class | Median leaky | Material | Found at the site |
|---|---|---|---|
| resample_label | 10.26 | 8/12 | 1/8 |
| same_bar | 7.21 | 20/20 | 0/20 |
| negative_shift | 6.77 | 12/12 | 6/12 |
| centered_rolling | 6.43 | 9/16 | 5/9 |
| reversed_cumulative | 2.42 | 12/16 | 6/12 |

The other ten classes have no material file. Events and fundamentals are independent of prices in
this data, so those classes cannot show a gain here. Of the 61 material files, monte-neo finds 17,
leakguard 10, peekproof 6, nofuturedata 6, overfit-gauntlet 5, lookahead-lint 4, backtest-audit 4,
and any linter 18.

## Examples

All under `corpus/v1/`. L0 leaks no tool finds at the site:

- `files/fd5996b1360.py:8`: `positions = signal`
- `files/f07bd3722e6.py:10`: `total += np.roll(returns, shift, axis=0)`
- `files/f178169036d.py:12`: `cut = int(len(close) * 1.0)`
- `files/fd6baad3d7c.py:7`: polars `cum_max(reverse=True)`; monte-neo finds the pandas and numpy
  forms, not this one
- `files/f416142bd2a.py:7`: polars `group_by_dynamic` with `label="left"`
- `files/f12808039d4.py:4`: `pivot_table(index="period_end")`

False positives on clean twins:

- `files/f272105f636.py:7`: monte-neo's full_sample_rank on a cross-sectional `rank(axis=1)`
- `files/f032dfffef6.py:23`: monte-neo's full_sample_stat on `nanmean(..., axis=1)`
- `files/fcd1b3331e2.py:14`: lookahead-lint, leakguard and overfit-gauntlet flag
  `shuffle=randomise` when `randomise` is False

## Localisation and stability

Flags mostly land on the site: all of them for six tools, 92/106 for monte-neo. That is on a site
line. The ±2-line measure is weak here, because a random code line scores 52 to 58% on these files.

Fresh generator seeds 101 and 202 give the same counts for every tool, except that peekproof flags
one more leaky and one more clean file. The any-linter row, the 3 unfound classes and the 8
surviving pairs are unchanged. These seeds change names and window lengths, not idioms, so they
cannot reveal tuning.

## Limitations

- **Synthetic scripts.** 6 to 37 lines, neutral style, no vendor APIs and no pnl line. Rules keyed
  to those forms have nothing to match, and rates describe this corpus, not code in the wild.
- **Mix.** Pooled rates are weighted by this corpus's classes and include L3, a level built to
  defeat syntactic rules.
- **Selection by the oracle.** A file enters only if the oracle agrees with its label, so leaks it
  cannot witness are absent. Recall here is recall on witnessable leaks.
- **Clean labels are evidence, not proof.**
- **Static tools only.** Runtime checks that several of these tools ship are not scored.
- **Read order.** Four tools were read before v1 was generated, so the templates may reflect their
  rules. Only overfit-gauntlet, monte-neo and nofuturedata are strictly out of sample.
- **Few clusters.** 30 templates is few for a percentile bootstrap, so the intervals are somewhat
  narrow.

## Reproduce

```sh
uv sync
uv run leakseed verify --workers 3
uv run leakseed impact
uv run leakseed score --tool all
uv run leakseed report
uv run python scripts/probes.py
```
