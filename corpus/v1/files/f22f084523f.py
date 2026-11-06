import json

import numpy as np

CONFIG = json.loads('{"stamp": "right"}')


def _to_weeks(volume, stamp):
    weekly = volume.resample("W-FRI", label=stamp, closed="left").mean()
    return weekly


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    volume = data["volume"]
    weekly = _to_weeks(volume, CONFIG["stamp"])
    daily = weekly.reindex(volume.index, method="ffill")
    surge = volume.ffill() / daily - 1.0
    signal = np.sign(returns) * surge.clip(-1.0, 1.0)
    positions = signal.shift(1)
    return positions
