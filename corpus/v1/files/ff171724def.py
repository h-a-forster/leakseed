import json

import numpy as np

CONFIG = json.loads('{"burn_in": 10}')


def _delayed(returns, burn_in):
    total = np.zeros_like(returns)
    for shift in range(1, 11):
        total += np.roll(returns, shift, axis=0)
    total[:burn_in] = np.nan
    return total


def run(data):
    close = data["close"].to_numpy()
    returns = np.full_like(close, np.nan)
    returns[1:] = close[1:] / close[:-1] - 1.0
    total = _delayed(returns, CONFIG["burn_in"])
    signal = np.sign(total / 10)
    positions = np.full_like(signal, np.nan)
    positions[1:] = signal[:-1]
    return positions
