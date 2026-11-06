import json

import numpy as np

CONFIG = json.loads('{"stat_window": "expanding"}')


def _score(level, stat_window):
    if stat_window == "full":
        score = level - np.nanmean(level, axis=0)
        return score
    score = level - np.nancumsum(level, axis=0) / np.cumsum(~np.isnan(level), axis=0)
    return score


def run(data):
    close = data["close"].to_numpy()
    returns = np.full_like(close, np.nan)
    returns[1:] = close[1:] / close[:-1] - 1.0
    level = np.log(close)
    score = _score(level, CONFIG["stat_window"])
    signal = -np.clip(score * 5.0, -1.0, 1.0)
    positions = np.full_like(signal, np.nan)
    positions[1:] = signal[:-1]
    return positions
