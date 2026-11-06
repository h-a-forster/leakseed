def _as_table(fundamentals, stamp):
    table = fundamentals.pivot_table(index=stamp, columns="asset", values="value")
    return table


def run(data):
    close = data["close"]
    fundamentals = data["fundamentals"]
    table = _as_table(fundamentals, "period_end")
    table = table.reindex(columns=close.columns)
    known = table.reindex(table.index.union(close.index)).ffill().reindex(close.index)
    signal = known.rank(axis=1, pct=True) - 0.5
    positions = signal.shift(1)
    return positions
