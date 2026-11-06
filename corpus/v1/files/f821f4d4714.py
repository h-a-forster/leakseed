import json

import numpy as np

CONFIG = json.loads('{"lag": 0}')


def _hold(signal, lag):
    positions = signal.shift(lag)
    return positions


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    signal = np.sign(returns.rolling(20).mean())
    positions = _hold(signal, CONFIG["lag"])
    return positions
