import pandas as pd


def run(data):
    close = data["close"]
    fundamentals = data["fundamentals"]
    grid = close.stack().rename("close").reset_index().astype({"asset": object})
    grid = grid.sort_values("date")
    book = fundamentals.sort_values("period_end")
    matched = pd.merge_asof(grid, book, left_on="date", right_on="period_end", by="asset")
    known = matched.pivot_table(index="date", columns="asset", values="value")
    known = known.reindex(index=close.index, columns=close.columns)
    signal = known.rank(axis=1, pct=True) - 0.5
    positions = signal.shift(1)
    return positions
