import numpy as np


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    signal = np.sign(returns.rolling(40).mean())
    positions = signal
    return positions
