import numpy as np


def run(data):
    close = data["close"].to_numpy()
    returns = np.full_like(close, np.nan)
    returns[1:] = close[1:] / close[:-1] - 1.0
    filled = np.nan_to_num(returns)
    lagged = np.roll(filled, 5, axis=0)
    signal = np.clip((filled - lagged) * 50.0, -1.0, 1.0)
    positions = np.full_like(signal, np.nan)
    positions[1:] = signal[:-1]
    return positions
