# Upstream reports

Issues filed with the scored linters from corpus v1 results: three misses and one false
positive. State read on 2026-11-21. The scorecard stays on monte-neo 0.54.0; v1's results are
frozen, so the two fixes below do not change them.

| Project | Issue | Filed | Finding | State |
| --- | --- | --- | --- | --- |
| monte-neo | [NeoZorK/Monte-Neo#124](https://github.com/NeoZorK/Monte-Neo/issues/124) | 2026-11-09 | Miss: Polars `fill_null(strategy="backward")`, `join_asof(strategy="forward")` and `cum_max(reverse=True)` pass the static lint; the pandas forms fail | Fixed in 0.55.0 (2026-11-20). Closed as completed on 2026-11-19 by PR #128 (merge commit 18bb051, contained in tag v0.55.0); the release notes list it: the three Polars forms now fail as `backward_fill`, `forward_asof` and `reversed_cumulative`, and their clean forms stay silent |
| peekproof | [Thesimpleex/peekproof#1](https://github.com/Thesimpleex/peekproof/issues/1) | 2026-11-09 | Miss: `resample(label="left", closed="right")` gets no PP008 | Open, no reply |
| nofuturedata | [ORANGINGS/nofuturedata#7](https://github.com/ORANGINGS/nofuturedata/issues/7) | 2026-11-09 | Miss: Polars `rolling_mean(center=True)` gets no SRC003; the pandas form does | Open, no reply |
| monte-neo | [NeoZorK/Monte-Neo#125](https://github.com/NeoZorK/Monte-Neo/issues/125) | 2026-11-12 | False positive: `full_sample_rank` and `full_sample_stat` fire on cross-sectional `axis=1` operations ([draft](upstream/monte-neo-cross-sectional-axis.md)) | Fixed in 0.55.0 (2026-11-20). The maintainer agreed on 2026-11-13; closed as completed on 2026-11-19 by the same PR #128 (18bb051, in tag v0.55.0). The release notes say both rules no longer warn on `axis=1` or `axis="columns"`, and still warn on `axis=0`, no axis, or a gather from the whole sample |

Not filed, decided 2026-11-12:

- [positive-roll-wraparound.md](upstream/positive-roll-wraparound.md): nofuturedata keeps a positive
  `np.roll` clean on purpose, and the leak is small (median absolute Sharpe 0.08, as for clean twins).
- [literal-flags-through-a-local.md](upstream/literal-flags-through-a-local.md): its targets are
  lookahead-lint, leakguard and overfit-gauntlet, which have no stars and were not reported to.
- [hand-rolled-parameter-selection.md](upstream/hand-rolled-parameter-selection.md): no linter claims
  this form, so it would be a large feature request with no sign of demand.
