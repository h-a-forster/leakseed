import polars as pl


def run(data):
    frame = pl.from_pandas(data["close"].reset_index())
    assets = [c for c in frame.columns if c != "date"]
    feature = frame.select(pl.col(assets).pct_change().shift(5))
    signal = feature.select(pl.all().rolling_mean(40).sign())
    positions = signal.select(pl.all().shift(1))
    return positions.to_numpy()
