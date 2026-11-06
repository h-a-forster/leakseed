import json

import numpy as np

CONFIG = json.loads('{"symmetric": false}')


def _window_stat(close, symmetric):
    smooth = close.rolling(21, center=symmetric).mean()
    return smooth


def run(data):
    close = data["close"]
    smooth = _window_stat(close, CONFIG["symmetric"])
    signal = np.sign(close - smooth)
    positions = signal.shift(1)
    return positions
