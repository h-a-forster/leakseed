import numpy as np


def run(data):
    close = data["close"].to_numpy()
    returns = np.full_like(close, np.nan)
    returns[1:] = close[1:] / close[:-1] - 1.0
    pad = 0
    total = np.zeros_like(returns)
    for shift in range(1, 21):
        total += np.roll(returns, shift, axis=0)
    total[:pad] = np.nan
    signal = np.sign(total / 20)
    positions = np.full_like(signal, np.nan)
    positions[1:] = signal[:-1]
    return positions
