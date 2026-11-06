import json

import numpy as np

CONFIG = json.loads('{"fill": "backward"}')


def _repair(volume, fill):
    if fill == "backward":
        filled = volume.bfill()
        return filled
    filled = volume.ffill()
    return filled


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    volume = data["volume"]
    filled = _repair(volume, CONFIG["fill"])
    surge = filled / filled.rolling(40).mean() - 1.0
    signal = np.sign(returns) * surge.clip(-1.0, 1.0)
    positions = signal.shift(1)
    return positions
