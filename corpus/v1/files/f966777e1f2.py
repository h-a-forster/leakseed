import polars as pl


def run(data):
    frame = pl.from_pandas(data["close"].reset_index())
    assets = [c for c in frame.columns if c != "date"]
    label = "left"
    weekly = frame.group_by_dynamic("date", every="1w", label=label, closed="left").agg(pl.col(assets).last())
    weekly = weekly.with_columns(pl.col(assets).pct_change())
    daily = frame.select("date").join_asof(weekly, on="date", strategy="backward")
    signal = daily.select(pl.col(assets).sign())
    positions = signal.select(pl.all().shift(1))
    return positions.to_numpy()
