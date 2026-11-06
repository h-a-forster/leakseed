import polars as pl


def run(data):
    frame = pl.from_pandas(data["close"].reset_index())
    assets = [c for c in frame.columns if c != "date"]
    momentum = frame.select(pl.col(assets).pct_change().rolling_mean(20))
    x = momentum
    score = x.select(pl.all() - pl.all().mean())
    signal = score.select((pl.all() * 100.0).clip(-1.0, 1.0))
    positions = signal.select(pl.all().shift(1))
    return positions.to_numpy()
