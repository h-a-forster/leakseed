import json

import polars as pl

CONFIG = json.loads('{"strategy": "linear"}')


def _fill_gaps(volume, assets, strategy):
    if strategy == "linear":
        filled = volume.select(pl.col(assets).interpolate())
        return filled
    filled = volume.select(pl.col(assets).fill_null(strategy="forward"))
    return filled


def run(data):
    frame = pl.from_pandas(data["close"].reset_index())
    assets = [c for c in frame.columns if c != "date"]
    volume = pl.from_pandas(data["volume"].reset_index())
    filled = _fill_gaps(volume, assets, CONFIG["strategy"])
    surge = filled.select(pl.all() / pl.all().rolling_mean(40) - 1.0)
    signal = pl.DataFrame([frame[c].pct_change().sign() * surge[c].clip(-1.0, 1.0) for c in assets])
    positions = signal.select(pl.all().shift(1))
    return positions.to_numpy()
