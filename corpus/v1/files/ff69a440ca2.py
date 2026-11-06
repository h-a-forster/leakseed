import numpy as np


def run(data):
    close = data["close"]
    signal = -np.sign(close / close.rolling(10).mean() - 1.0)
    positions = signal.shift(1)
    return positions
