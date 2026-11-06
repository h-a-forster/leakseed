import json

import numpy as np

CONFIG = json.loads('{"scan": "reverse"}')


def _envelope(volume, scan):
    if scan == "reverse":
        cumulative = volume[::-1].cumsum()[::-1]
        return cumulative
    cumulative = volume.cumsum()
    return cumulative


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    volume = data["volume"]
    cumulative = _envelope(volume, CONFIG["scan"])
    signal = np.sign(returns) * (volume / cumulative * 100.0).clip(0.0, 1.0)
    positions = signal.shift(1)
    return positions
