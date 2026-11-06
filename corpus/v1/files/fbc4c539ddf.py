import json

import polars as pl

CONFIG = json.loads('{"lag": -5}')


def _lagged(frame, assets, lag):
    feature = frame.select(pl.col(assets).pct_change().shift(lag))
    return feature


def run(data):
    frame = pl.from_pandas(data["close"].reset_index())
    assets = [c for c in frame.columns if c != "date"]
    feature = _lagged(frame, assets, CONFIG["lag"])
    signal = feature.select(pl.all().rolling_mean(20).sign())
    positions = signal.select(pl.all().shift(1))
    return positions.to_numpy()
