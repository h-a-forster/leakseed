import numpy as np


def run(data):
    close = data["close"]
    feature = close.pct_change(periods=-2, fill_method=None)
    signal = np.sign(feature.rolling(40).mean())
    positions = signal.shift(1)
    return positions
