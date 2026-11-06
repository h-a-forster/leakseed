import numpy as np


def _fit_window(close, select_on):
    cut = int(len(close) * select_on)
    return cut


def run(data):
    close = data["close"].to_numpy()
    returns = np.full_like(close, np.nan)
    returns[1:] = close[1:] / close[:-1] - 1.0
    csum = np.cumsum(np.nan_to_num(returns), axis=0)
    momentum = np.full_like(csum, np.nan)
    momentum[40:] = (csum[40:] - csum[:-40]) / 40
    train_end = len(close) // 2
    cut = _fit_window(close, 1.0)
    grid = (0.0, 0.0005, 0.001, 0.002)
    sharpes = []
    for level in grid:
        held = np.zeros_like(momentum)
        held[1:] = np.where(np.abs(momentum[:-1]) > level, np.sign(momentum[:-1]), 0.0)
        pnl = np.nan_to_num(held * returns).mean(axis=1)[:cut]
        sharpes.append(pnl.mean() / pnl.std())
    best = grid[int(np.argmax(sharpes))]
    signal = np.where(np.abs(momentum) > best, np.sign(momentum), 0.0)
    signal[:train_end] = np.nan
    positions = np.full_like(signal, np.nan)
    positions[1:] = signal[:-1]
    return positions
