import numpy as np


def run(data):
    close = data["close"]
    horizon = 1
    feature = close.pct_change(periods=horizon, fill_method=None)
    signal = np.sign(feature.rolling(20).mean())
    positions = signal.shift(1)
    return positions
