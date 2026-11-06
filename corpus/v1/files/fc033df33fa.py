import numpy as np


def _lagged(returns, lag):
    feature = returns.shift(lag)
    return feature


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    feature = _lagged(returns, -5)
    signal = np.sign(feature.rolling(40).mean())
    positions = signal.shift(1)
    return positions
