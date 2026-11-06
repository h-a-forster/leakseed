import numpy as np


def run(data):
    close = data["close"]
    signal = -np.sign(close / close.rolling(10).mean() - 1.0)
    execution_lag = 0
    positions = signal.shift(execution_lag)
    return positions
