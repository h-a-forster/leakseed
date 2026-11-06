import numpy as np


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    periods = -2
    feature = returns.shift(periods)
    signal = np.sign(feature.rolling(20).mean())
    positions = signal.shift(1)
    return positions
