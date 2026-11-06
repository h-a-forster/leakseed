import numpy as np


def run(data):
    close = data["close"].to_numpy()
    returns = np.full_like(close, np.nan)
    returns[1:] = close[1:] / close[:-1] - 1.0
    feature = np.roll(np.nan_to_num(returns), 1, axis=0)
    feature[:1] = np.nan
    positions = np.full_like(feature, np.nan)
    positions[1:] = np.sign(feature[:-1])
    return positions
