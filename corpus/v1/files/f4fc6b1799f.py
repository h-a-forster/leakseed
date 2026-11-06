import numpy as np


def _to_positions(signal, lag):
    positions = signal.shift(lag)
    return positions


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    signal = np.sign(returns.rolling(20).mean())
    positions = _to_positions(signal, 1)
    return positions
