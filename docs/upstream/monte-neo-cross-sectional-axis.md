# Draft: monte-neo warns on cross-sectional operations

Not filed. Applies to monte-neo 0.54.0, `monte_neo/verify/lint.py`.

`full_sample_rank` and `full_sample_stat` do not look at `axis`. `rank(axis=1)` and
`np.nanmean(x, axis=1)` compute over the assets of one row, so they read no later row:

    signal = known.rank(axis=1, pct=True) - 0.5          # corpus/v1/files/f05d500efe7.py:13
    market[1:] = np.nanmean(returns[1:], axis=1)         # corpus/v1/files/f032dfffef6.py:23

In corpus v1 these two rules, with `group_aggregate` on `resample` chains, are most of the 58
flagged clean files out of 184. They are warnings: at the `fail` severity alone the
false-positive rate is 8/184. The same warnings add file-level recall in classes where no rule
sees the leak, and in `restatement_overwrite` they mask a hit at the site in the file-level
paired measure.

Suggested fix: skip both rules when `axis=1` or `axis="columns"` is passed. `_grouped_by_timestamp`
already makes the same exception for per-timestamp groups.
