import numpy as np


def _delayed(filled, warmup):
    lagged = np.roll(filled, 2, axis=0)
    lagged[:warmup] = np.nan
    return lagged


def run(data):
    close = data["close"].to_numpy()
    returns = np.full_like(close, np.nan)
    returns[1:] = close[1:] / close[:-1] - 1.0
    filled = np.nan_to_num(returns)
    lagged = _delayed(filled, 2)
    signal = np.clip((filled - lagged) * 50.0, -1.0, 1.0)
    positions = np.full_like(signal, np.nan)
    positions[1:] = signal[:-1]
    return positions
