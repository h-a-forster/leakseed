import json

import polars as pl

CONFIG = json.loads('{"gap_rule": "backward"}')


def _repair(volume, assets, gap_rule):
    filled = volume.select(pl.col(assets).fill_null(strategy=gap_rule))
    return filled


def run(data):
    frame = pl.from_pandas(data["close"].reset_index())
    assets = [c for c in frame.columns if c != "date"]
    volume = pl.from_pandas(data["volume"].reset_index())
    filled = _repair(volume, assets, CONFIG["gap_rule"])
    surge = filled.select(pl.all() / pl.all().rolling_mean(20) - 1.0)
    signal = pl.DataFrame([frame[c].pct_change().sign() * surge[c].clip(-1.0, 1.0) for c in assets])
    positions = signal.select(pl.all().shift(1))
    return positions.to_numpy()
