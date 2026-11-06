import json

CONFIG = json.loads('{"scaling": "full"}')


def _normalise(momentum, scaling):
    if scaling == "full":
        score = (momentum - momentum.mean()) / momentum.std()
        return score
    score = (momentum - momentum.expanding().mean()) / momentum.expanding().std()
    return score


def run(data):
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    momentum = returns.rolling(10).mean()
    score = _normalise(momentum, CONFIG["scaling"])
    signal = score.clip(-2.0, 2.0)
    positions = signal.shift(1)
    return positions
