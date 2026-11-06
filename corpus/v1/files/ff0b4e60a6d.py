import polars as pl


def _align_filings(calendar, fundamentals, key):
    table = fundamentals.pivot(on="asset", index=key, values="value", aggregate_function="mean").sort(key)
    known = calendar.join_asof(table, left_on="date", right_on=key, strategy="backward")
    return known


def run(data):
    assets = list(data["close"].columns)
    calendar = pl.from_pandas(data["close"].reset_index()).select("date")
    fundamentals = pl.from_pandas(data["fundamentals"])
    known = _align_filings(calendar, fundamentals, "filed")
    signal = known.select([pl.col(c) - pl.mean_horizontal(assets) for c in assets])
    positions = signal.select(pl.all().shift(1))
    return positions.to_numpy()
