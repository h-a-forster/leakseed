# Draft: `np.roll` with a positive shift also leaks

Not filed. Applies to peekproof (PP001), monte-neo (`negative_roll`) and nofuturedata (SRC012).

All three flag `np.roll(x, -1)`. A positive shift is a lag on every row but the first k, and
those rows receive the last k rows of the sample, which are the future. No tool flags that.

    lagged = np.roll(filled, 2, axis=0)   # lagged[:2] holds the last two rows

Corpus v1 has 8 such leaky files (`np_roll`), confirmed by the causality oracle, for example
`corpus/v1/files/f07bd3722e6.py:10`. Recall at the site is 0/8 for every tool. The clean twin
assigns `lagged[:k] = np.nan` after the roll.

Suggested check: a `roll` along the time axis whose wrapped rows are not overwritten or masked
before use. Positive shifts cannot be told from a harmless circular operation in general, so a
low-confidence finding fits. The leak moves only the first k rows of the output, so it is small
in practice (corpus median |Sharpe| 0.08, the same as the clean twins).
