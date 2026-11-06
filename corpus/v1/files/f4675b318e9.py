import numpy as np


def _high_water(volume):
    cumulative = volume.cumsum()
    return cumulative


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    volume = data["volume"]
    cumulative = _high_water(volume)
    signal = np.sign(returns) * (volume / cumulative * 100.0).clip(0.0, 1.0)
    positions = signal.shift(1)
    return positions
