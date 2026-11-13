# Upstream reports

Issues filed with the scored linters from corpus v1 results: three misses and one false
positive. State read on 2026-11-13.

| Project | Issue | Filed | Finding | State |
| --- | --- | --- | --- | --- |
| monte-neo | [NeoZorK/Monte-Neo#124](https://github.com/NeoZorK/Monte-Neo/issues/124) | 2026-11-09 | Miss: Polars `fill_null(strategy="backward")`, `join_asof(strategy="forward")` and `cum_max(reverse=True)` pass the static lint; the pandas forms fail | Open. The maintainer replied the same day that he will review the cases and, if they check out, add support with regression tests in a future release; the latest release is still 0.54.0 |
| peekproof | [Thesimpleex/peekproof#1](https://github.com/Thesimpleex/peekproof/issues/1) | 2026-11-09 | Miss: `resample(label="left", closed="right")` gets no PP008 | Open, no reply |
| nofuturedata | [ORANGINGS/nofuturedata#7](https://github.com/ORANGINGS/nofuturedata/issues/7) | 2026-11-09 | Miss: Polars `rolling_mean(center=True)` gets no SRC003; the pandas form does | Open, no reply |
| monte-neo | [NeoZorK/Monte-Neo#125](https://github.com/NeoZorK/Monte-Neo/issues/125) | 2026-11-12 | False positive: `full_sample_rank` and `full_sample_stat` fire on cross-sectional `axis=1` operations ([draft](upstream/monte-neo-cross-sectional-axis.md)) | Open, no reply |

Not filed, decided 2026-11-12:

- [positive-roll-wraparound.md](upstream/positive-roll-wraparound.md): nofuturedata keeps a positive
  `np.roll` clean on purpose, and the leak is small (median absolute Sharpe 0.08, as for clean twins).
- [literal-flags-through-a-local.md](upstream/literal-flags-through-a-local.md): its targets are
  lookahead-lint, leakguard and overfit-gauntlet, which have no stars and were not reported to.
- [hand-rolled-parameter-selection.md](upstream/hand-rolled-parameter-selection.md): no linter claims
  this form, so it would be a large feature request with no sign of demand.
