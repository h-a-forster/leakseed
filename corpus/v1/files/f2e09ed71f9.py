import numpy as np


def _high_water(close):
    peak = np.fmax.accumulate(close, axis=0)
    return peak


def run(data):
    close = data["close"].to_numpy()
    returns = np.full_like(close, np.nan)
    returns[1:] = close[1:] / close[:-1] - 1.0
    peak = _high_water(close)
    signal = np.clip(1.0 + 5.0 * (close / peak - 1.0), 0.0, None)
    positions = np.full_like(signal, np.nan)
    positions[1:] = signal[:-1]
    return positions
