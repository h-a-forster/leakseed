import json

import numpy as np

CONFIG = json.loads('{"stamp": "left"}')


def _weekly(close, stamp):
    weekly = close.resample("W-FRI", label=stamp, closed="right").last()
    return weekly


def run(data):
    close = data["close"]
    weekly = _weekly(close, CONFIG["stamp"])
    daily = weekly.pct_change(fill_method=None).reindex(close.index, method="ffill")
    signal = np.sign(daily)
    positions = signal.shift(1)
    return positions
