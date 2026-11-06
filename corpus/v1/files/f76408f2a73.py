import numpy as np


def _align_feature(close, horizon):
    feature = close.pct_change(periods=horizon, fill_method=None)
    return feature


def run(data):
    close = data["close"]
    feature = _align_feature(close, -1)
    signal = np.sign(feature.rolling(20).mean())
    positions = signal.shift(1)
    return positions
