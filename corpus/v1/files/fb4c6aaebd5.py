import numpy as np


def run(data):
    close = data["close"]
    center = False
    smooth = close.rolling(21, center=center).mean()
    signal = np.sign(close - smooth)
    positions = signal.shift(1)
    return positions
