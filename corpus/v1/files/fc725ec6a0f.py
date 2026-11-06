import json

import numpy as np

CONFIG = json.loads('{"symmetric": false}')


def _window_stat(returns, symmetric):
    vol = returns.rolling(21, center=symmetric).std()
    return vol


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    vol = _window_stat(returns, CONFIG["symmetric"])
    signal = np.sign(returns.rolling(5).mean()) * 0.01 / vol
    positions = signal.shift(1)
    return positions
