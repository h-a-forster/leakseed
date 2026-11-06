import polars as pl


def _bin_weeks(frame, assets, stamp):
    weekly = frame.group_by_dynamic("date", every="1w", label=stamp, closed="left").agg(pl.col(assets).last())
    return weekly


def run(data):
    frame = pl.from_pandas(data["close"].reset_index())
    assets = [c for c in frame.columns if c != "date"]
    weekly = _bin_weeks(frame, assets, "right")
    weekly = weekly.with_columns(pl.col(assets).pct_change())
    daily = frame.select("date").join_asof(weekly, on="date", strategy="backward")
    signal = daily.select(pl.col(assets).sign())
    positions = signal.select(pl.all().shift(1))
    return positions.to_numpy()
