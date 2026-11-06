import json

import numpy as np

CONFIG = json.loads('{"lag": 2}')


def _lagged(close, lag):
    feature = close.pct_change(periods=lag, fill_method=None)
    return feature


def run(data):
    close = data["close"]
    feature = _lagged(close, CONFIG["lag"])
    signal = np.sign(feature.rolling(20).mean())
    positions = signal.shift(1)
    return positions
