import numpy as np


def _execute(signal, delay):
    positions = np.full_like(signal, np.nan)
    positions[delay:] = signal[: len(signal) - delay]
    return positions


def run(data):
    close = data["close"].to_numpy()
    returns = np.full_like(close, np.nan)
    returns[1:] = close[1:] / close[:-1] - 1.0
    csum = np.cumsum(np.nan_to_num(returns), axis=0)
    momentum = np.full_like(csum, np.nan)
    momentum[20:] = (csum[20:] - csum[:-20]) / 20
    signal = np.sign(momentum)
    positions = _execute(signal, 1)
    return positions
