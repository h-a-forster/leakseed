import numpy as np


def _smooth(close, centered):
    smooth = close.rolling(5, center=centered).mean()
    return smooth


def run(data):
    close = data["close"]
    smooth = _smooth(close, True)
    signal = np.sign(close - smooth)
    positions = signal.shift(1)
    return positions
