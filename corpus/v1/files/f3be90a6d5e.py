import numpy as np
from sklearn.preprocessing import StandardScaler


def _normalise(features, fit_fraction):
    scaler = StandardScaler().fit(features[: int(len(features) * fit_fraction)])
    return scaler


def run(data):
    close = data["close"].to_numpy()
    returns = np.full_like(close, np.nan)
    returns[1:] = close[1:] / close[:-1] - 1.0
    features = np.nan_to_num(returns)
    train_end = len(features) // 2
    scaler = _normalise(features, 0.5)
    signal = -np.clip(scaler.transform(features), -2.0, 2.0)
    signal[:train_end] = np.nan
    positions = np.full_like(signal, np.nan)
    positions[1:] = signal[:-1]
    return positions
