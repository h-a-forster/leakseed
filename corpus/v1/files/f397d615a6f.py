import polars as pl


def run(data):
    frame = pl.from_pandas(data["close"].reset_index())
    assets = [c for c in frame.columns if c != "date"]
    signal = frame.select(pl.col(assets).pct_change().rolling_mean(40).sign())
    lag = 0
    positions = signal.select(pl.all().shift(lag))
    return positions.to_numpy()
