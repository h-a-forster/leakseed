import numpy as np
from sklearn.model_selection import TimeSeriesSplit


def run(data):
    close = data["close"].to_numpy()
    returns = np.full_like(close, np.nan)
    returns[1:] = close[1:] / close[:-1] - 1.0
    n = len(close)
    market = np.zeros(n)
    market[1:] = np.nanmean(returns[1:], axis=1)
    lags = np.full((n, 3), np.nan)
    now = np.full((n, 3), np.nan)
    for k in (1, 2, 3):
        lags[k:, k - 1] = market[:-k]
        now[k - 1 :, k - 1] = market[: n - k + 1]
    rows = np.arange(3, n)
    idx = rows
    folds = list(TimeSeriesSplit(n_splits=5).split(idx))
    signal = np.full(n, np.nan)
    for train, test in folds:
        coef, *_ = np.linalg.lstsq(lags[rows[train]], market[rows[train]], rcond=None)
        signal[rows[test]] = now[rows[test]] @ coef
    positions = np.full_like(signal, np.nan)
    positions[1:] = signal[:-1]
    return positions
