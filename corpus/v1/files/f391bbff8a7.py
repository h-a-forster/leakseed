import numpy as np


def run(data):
    close = data["close"].to_numpy()
    returns = np.full_like(close, np.nan)
    returns[1:] = close[1:] / close[:-1] - 1.0
    csum = np.cumsum(np.nan_to_num(returns), axis=0)
    momentum = np.full_like(csum, np.nan)
    momentum[40:] = (csum[40:] - csum[:-40]) / 40
    signal = np.sign(momentum)
    lag = 0
    positions = np.full_like(signal, np.nan)
    positions[lag:] = signal[: len(signal) - lag]
    return positions
