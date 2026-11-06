import polars as pl


def run(data):
    frame = pl.from_pandas(data["close"].reset_index())
    assets = [c for c in frame.columns if c != "date"]
    centered = False
    signal = frame.select([(pl.col(c) - pl.col(c).rolling_mean(21, center=centered)).sign() for c in assets])
    positions = signal.select(pl.all().shift(1))
    return positions.to_numpy()
