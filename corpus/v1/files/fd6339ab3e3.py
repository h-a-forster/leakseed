import json

import polars as pl

CONFIG = json.loads('{"center": true}')


def _rolling_view(frame, assets, center):
    signal = frame.select([(pl.col(c) - pl.col(c).rolling_mean(5, center=center)).sign() for c in assets])
    return signal


def run(data):
    frame = pl.from_pandas(data["close"].reset_index())
    assets = [c for c in frame.columns if c != "date"]
    signal = _rolling_view(frame, assets, CONFIG["center"])
    positions = signal.select(pl.all().shift(1))
    return positions.to_numpy()
