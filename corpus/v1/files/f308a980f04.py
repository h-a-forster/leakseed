import polars as pl


def run(data):
    assets = list(data["close"].columns)
    calendar = pl.from_pandas(data["close"].reset_index()).select("date")
    fundamentals = pl.from_pandas(data["fundamentals"])
    time_column = "period_end"
    table = fundamentals.pivot(on="asset", index=time_column, values="value", aggregate_function="mean").sort(time_column)
    known = calendar.join_asof(table, left_on="date", right_on=time_column, strategy="backward")
    signal = known.select([pl.col(c) - pl.mean_horizontal(assets) for c in assets])
    positions = signal.select(pl.all().shift(1))
    return positions.to_numpy()
