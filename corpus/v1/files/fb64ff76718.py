import numpy as np


def _fill_gaps(volume):
    filled = volume.ffill()
    return filled


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    volume = data["volume"]
    filled = _fill_gaps(volume)
    surge = filled / filled.rolling(20).mean() - 1.0
    signal = np.sign(returns) * surge.clip(-1.0, 1.0)
    positions = signal.shift(1)
    return positions
