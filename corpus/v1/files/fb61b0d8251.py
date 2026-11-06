import json

import numpy as np

CONFIG = json.loads('{"gap_rule": "linear"}')


def _fill_gaps(volume, gap_rule):
    if gap_rule == "linear":
        filled = volume.interpolate()
        return filled
    filled = volume.ffill()
    return filled


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    volume = data["volume"]
    filled = _fill_gaps(volume, CONFIG["gap_rule"])
    surge = filled / filled.rolling(20).mean() - 1.0
    signal = np.sign(returns) * surge.clip(-1.0, 1.0)
    positions = signal.shift(1)
    return positions
