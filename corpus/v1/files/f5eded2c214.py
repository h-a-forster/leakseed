import numpy as np


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    signal = np.sign(returns.rolling(10).mean())
    execution_lag = 1
    positions = signal.shift(execution_lag)
    return positions
