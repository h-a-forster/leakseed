import numpy as np


def _selection_end(close, select_on):
    cut = int(len(close) * select_on)
    return cut


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    train_end = len(close) // 2
    candidates = {}
    pnls = {}
    for window in (5, 10, 20, 40):
        candidates[window] = np.sign(returns.rolling(window).mean())
        pnls[window] = (candidates[window].shift(1) * returns).mean(axis=1)
    cut = _selection_end(close, 0.5)
    scores = {w: s.iloc[:cut].mean() / s.iloc[:cut].std() for w, s in pnls.items()}
    best = max(scores, key=scores.get)
    signal = candidates[best].copy()
    signal.iloc[:train_end] = np.nan
    positions = signal.shift(1)
    return positions
