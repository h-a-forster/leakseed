import json

import numpy as np

CONFIG = json.loads('{"execution_lag": 1}')


def _to_positions(signal, execution_lag):
    positions = signal.shift(execution_lag)
    return positions


def run(data):
    close = data["close"]
    signal = -np.sign(close / close.rolling(40).mean() - 1.0)
    positions = _to_positions(signal, CONFIG["execution_lag"])
    return positions
