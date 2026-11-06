import numpy as np


def _past(returns, warmup):
    total = np.zeros_like(returns)
    for shift in range(1, 11):
        total += np.roll(returns, shift, axis=0)
    total[:warmup] = np.nan
    return total


def run(data):
    close = data["close"].to_numpy()
    returns = np.full_like(close, np.nan)
    returns[1:] = close[1:] / close[:-1] - 1.0
    total = _past(returns, 0)
    signal = np.sign(total / 10)
    positions = np.full_like(signal, np.nan)
    positions[1:] = signal[:-1]
    return positions
