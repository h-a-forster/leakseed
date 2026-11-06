import numpy as np


def _rolling_view(returns, symmetric):
    vol = returns.rolling(21, center=symmetric).std()
    return vol


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    vol = _rolling_view(returns, False)
    signal = np.sign(returns.rolling(5).mean()) * 0.01 / vol
    positions = signal.shift(1)
    return positions
