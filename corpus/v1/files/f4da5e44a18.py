import numpy as np


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    volume = data["volume"]
    stamp = "right"
    weekly = volume.resample("W-FRI", label=stamp, closed="left").mean()
    daily = weekly.reindex(volume.index, method="ffill")
    surge = volume.ffill() / daily - 1.0
    signal = np.sign(returns) * surge.clip(-1.0, 1.0)
    positions = signal.shift(1)
    return positions
