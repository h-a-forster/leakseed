import polars as pl


def _smooth(frame, assets, symmetric):
    signal = frame.select([(pl.col(c) - pl.col(c).rolling_mean(11, center=symmetric)).sign() for c in assets])
    return signal


def run(data):
    frame = pl.from_pandas(data["close"].reset_index())
    assets = [c for c in frame.columns if c != "date"]
    signal = _smooth(frame, assets, False)
    positions = signal.select(pl.all().shift(1))
    return positions.to_numpy()
