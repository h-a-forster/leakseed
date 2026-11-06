import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    market = returns.mean(axis=1)
    lags = pd.concat({k: market.shift(k) for k in (1, 2, 3)}, axis=1)
    now = pd.concat({k: market.shift(k - 1) for k in (1, 2, 3)}, axis=1)
    rows = np.flatnonzero(lags.notna().all(axis=1).to_numpy())
    train, test = train_test_split(rows, test_size=0.3, shuffle=False, random_state=0)
    coef, *_ = np.linalg.lstsq(lags.to_numpy()[train], market.to_numpy()[train], rcond=None)
    forecast = now.to_numpy() @ coef
    signal = pd.Series(np.nan, index=close.index)
    signal.iloc[test] = forecast[test]
    positions = signal.shift(1)
    return positions
