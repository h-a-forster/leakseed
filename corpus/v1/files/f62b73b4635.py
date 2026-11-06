import numpy as np


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    center = False
    vol = returns.rolling(11, center=center).std()
    signal = np.sign(returns.rolling(5).mean()) * 0.01 / vol
    positions = signal.shift(1)
    return positions
