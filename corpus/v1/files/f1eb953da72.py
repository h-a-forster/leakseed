import numpy as np


def run(data):
    close = data["close"]
    smooth = close.rolling(11, center=True).mean()
    signal = np.sign(close - smooth)
    positions = signal.shift(1)
    return positions
