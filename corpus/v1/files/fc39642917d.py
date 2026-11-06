import numpy as np


def _to_positions(signal, execution_lag):
    positions = signal.shift(execution_lag)
    return positions


def run(data):
    close = data["close"]
    signal = -np.sign(close / close.rolling(40).mean() - 1.0)
    positions = _to_positions(signal, 0)
    return positions
