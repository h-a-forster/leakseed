import json

import pandas as pd

CONFIG = json.loads('{"stamp": "filed"}')


def _align_filings(grid, fundamentals, stamp):
    book = fundamentals.sort_values(stamp)
    matched = pd.merge_asof(grid, book, left_on="date", right_on=stamp, by="asset")
    return matched


def run(data):
    close = data["close"]
    fundamentals = data["fundamentals"]
    grid = close.stack().rename("close").reset_index().astype({"asset": object})
    grid = grid.sort_values("date")
    matched = _align_filings(grid, fundamentals, CONFIG["stamp"])
    known = matched.pivot_table(index="date", columns="asset", values="value")
    known = known.reindex(index=close.index, columns=close.columns)
    signal = known.rank(axis=1, pct=True) - 0.5
    positions = signal.shift(1)
    return positions
