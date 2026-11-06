import numpy as np


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    volume = data["volume"]
    prices = volume
    cumulative = prices[::-1].cumsum()[::-1]
    signal = np.sign(returns) * (volume / cumulative * 100.0).clip(0.0, 1.0)
    positions = signal.shift(1)
    return positions
