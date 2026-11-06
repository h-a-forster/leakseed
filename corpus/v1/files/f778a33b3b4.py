import json

import numpy as np

CONFIG = json.loads('{"lag": 3}')


def _lagged(returns, lag):
    feature = returns.shift(lag)
    return feature


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    feature = _lagged(returns, CONFIG["lag"])
    signal = np.sign(feature.rolling(10).mean())
    positions = signal.shift(1)
    return positions
