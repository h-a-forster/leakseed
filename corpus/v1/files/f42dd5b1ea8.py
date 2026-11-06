import json

import polars as pl

CONFIG = json.loads('{"symmetric": false}')


def _window_stat(frame, assets, symmetric):
    signal = frame.select([(0.01 / pl.col(c).pct_change().rolling_std(5, center=symmetric)).alias(c) for c in assets])
    return signal


def run(data):
    frame = pl.from_pandas(data["close"].reset_index())
    assets = [c for c in frame.columns if c != "date"]
    signal = _window_stat(frame, assets, CONFIG["symmetric"])
    positions = signal.select(pl.all().shift(1))
    return positions.to_numpy()
