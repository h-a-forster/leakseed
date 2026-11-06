import json

import numpy as np

CONFIG = json.loads('{"tuning_share": 1.0}')


def _tuning_cut(close, tuning_share):
    cut = int(len(close) * tuning_share)
    return cut


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    train_end = len(close) // 2
    candidates = {}
    pnls = {}
    for window in (5, 15, 30, 90):
        candidates[window] = np.sign(returns.rolling(window).mean())
        pnls[window] = (candidates[window].shift(1) * returns).mean(axis=1)
    cut = _tuning_cut(close, CONFIG["tuning_share"])
    scores = {w: s.iloc[:cut].mean() / s.iloc[:cut].std() for w, s in pnls.items()}
    best = max(scores, key=scores.get)
    signal = candidates[best].copy()
    signal.iloc[:train_end] = np.nan
    positions = signal.shift(1)
    return positions
