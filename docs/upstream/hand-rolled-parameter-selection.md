# Draft: parameters chosen by a hand-written search over the full sample

Not filed. Applies to all seven linters scored by leakseed.

Four tools flag `GridSearchCV` with a time-blind split (`corpus/probes`,
`results/v1/probes.md`). The usual backtest form is a loop, and no tool flags it:

    sharpes = []
    for level in grid:
        ...
        pnl = np.nan_to_num(held * returns).mean(axis=1)[:cut]   # cut = len(close)
        sharpes.append(pnl.mean() / pnl.std())
    best = grid[int(np.argmax(sharpes))]

Corpus v1 has 8 such leaky files (`argmax_param`), for example
`corpus/v1/files/f178169036d.py:12`. Their clean twins select on the first half and trade the
second. monte-neo flags `pnl.mean()` in both twins, so at the site every tool scores 0/8.

Suggested check: `max`, `argmax` or `idxmax` over a performance statistic computed inside a loop
or comprehension, when the statistic's range reaches the bars the chosen value trades. That
needs the slice bound, so a constant-fold pass helps (`int(len(close) * 1.0)`).
