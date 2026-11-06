import json

import numpy as np
from sklearn.preprocessing import StandardScaler

CONFIG = json.loads('{"in_sample": 0.5}')


def _standardise(features, in_sample):
    scaler = StandardScaler().fit(features[: int(len(features) * in_sample)])
    return scaler


def run(data):
    close = data["close"].to_numpy()
    returns = np.full_like(close, np.nan)
    returns[1:] = close[1:] / close[:-1] - 1.0
    features = np.nan_to_num(returns)
    train_end = len(features) // 2
    scaler = _standardise(features, CONFIG["in_sample"])
    signal = -np.clip(scaler.transform(features), -2.0, 2.0)
    signal[:train_end] = np.nan
    positions = np.full_like(signal, np.nan)
    positions[1:] = signal[:-1]
    return positions
