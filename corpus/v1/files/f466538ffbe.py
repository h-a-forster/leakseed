import polars as pl


def run(data):
    frame = pl.from_pandas(data["close"].reset_index())
    assets = [c for c in frame.columns if c != "date"]
    signal = frame.select([(0.01 / pl.col(c).pct_change().rolling_std(11, center=False)).alias(c) for c in assets])
    positions = signal.select(pl.all().shift(1))
    return positions.to_numpy()
