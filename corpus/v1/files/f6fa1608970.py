import json

import polars as pl

CONFIG = json.loads('{"fit_span": "full"}')


def _normalise(momentum, fit_span):
    if fit_span == "full":
        score = momentum.select(pl.all() - pl.all().mean())
        return score
    score = momentum.select(pl.all() - pl.all().cum_sum() / pl.all().cum_count())
    return score


def run(data):
    frame = pl.from_pandas(data["close"].reset_index())
    assets = [c for c in frame.columns if c != "date"]
    momentum = frame.select(pl.col(assets).pct_change().rolling_mean(40))
    score = _normalise(momentum, CONFIG["fit_span"])
    signal = score.select((pl.all() * 100.0).clip(-1.0, 1.0))
    positions = signal.select(pl.all().shift(1))
    return positions.to_numpy()
