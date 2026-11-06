import numpy as np


def run(data):
    close = data["close"].to_numpy()
    returns = np.full_like(close, np.nan)
    returns[1:] = close[1:] / close[:-1] - 1.0
    csum = np.cumsum(np.nan_to_num(returns), axis=0)
    momentum = np.full_like(csum, np.nan)
    momentum[20:] = (csum[20:] - csum[:-20]) / 20
    signal = -np.clip(momentum * 100.0, -1.0, 1.0)
    execution_lag = 1
    positions = np.full_like(signal, np.nan)
    positions[execution_lag:] = signal[: len(signal) - execution_lag]
    return positions
