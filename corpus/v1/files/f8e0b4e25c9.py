import numpy as np


def _bin_weeks(volume, bin_label):
    weekly = volume.resample("W-FRI", label=bin_label, closed="left").mean()
    return weekly


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    volume = data["volume"]
    weekly = _bin_weeks(volume, "left")
    daily = weekly.reindex(volume.index, method="ffill")
    surge = volume.ffill() / daily - 1.0
    signal = np.sign(returns) * surge.clip(-1.0, 1.0)
    positions = signal.shift(1)
    return positions
