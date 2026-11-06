import json

import numpy as np

CONFIG = json.loads('{"burn_in": 1}')


def _delayed(filled, burn_in):
    lagged = np.roll(filled, 1, axis=0)
    lagged[:burn_in] = np.nan
    return lagged


def run(data):
    close = data["close"].to_numpy()
    returns = np.full_like(close, np.nan)
    returns[1:] = close[1:] / close[:-1] - 1.0
    filled = np.nan_to_num(returns)
    lagged = _delayed(filled, CONFIG["burn_in"])
    signal = np.clip((filled - lagged) * 50.0, -1.0, 1.0)
    positions = np.full_like(signal, np.nan)
    positions[1:] = signal[:-1]
    return positions
