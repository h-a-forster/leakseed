import json

import numpy as np

CONFIG = json.loads('{"execution_lag": 0}')


def _execute(signal, execution_lag):
    positions = np.full_like(signal, np.nan)
    positions[execution_lag:] = signal[: len(signal) - execution_lag]
    return positions


def run(data):
    close = data["close"].to_numpy()
    returns = np.full_like(close, np.nan)
    returns[1:] = close[1:] / close[:-1] - 1.0
    csum = np.cumsum(np.nan_to_num(returns), axis=0)
    momentum = np.full_like(csum, np.nan)
    momentum[10:] = (csum[10:] - csum[:-10]) / 10
    signal = np.sign(momentum)
    positions = _execute(signal, CONFIG["execution_lag"])
    return positions
