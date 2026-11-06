import polars as pl


def run(data):
    assets = list(data["close"].columns)
    calendar = pl.from_pandas(data["close"].reset_index()).select("date")
    fundamentals = pl.from_pandas(data["fundamentals"])
    table = fundamentals.pivot(on="asset", index="period_end", values="value", aggregate_function="mean").sort("period_end")
    known = calendar.join_asof(table, left_on="date", right_on="period_end", strategy="backward")
    signal = known.select([pl.col(c) - pl.mean_horizontal(assets) for c in assets])
    positions = signal.select(pl.all().shift(1))
    return positions.to_numpy()
