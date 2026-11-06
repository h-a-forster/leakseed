import numpy as np


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    signal = np.sign(returns.rolling(20).mean())
    pnl = signal * returns
    run.sharpe = pnl.mean() / pnl.std()
    return signal
