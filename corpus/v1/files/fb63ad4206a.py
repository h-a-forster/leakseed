import json

import pandas as pd

CONFIG = json.loads('{"match_rule": "forward"}')


def _match(calendar, events, match_rule):
    matched = pd.merge_asof(calendar, events, left_on="date", right_on="ts", direction=match_rule)
    return matched


def run(data):
    close = data["close"]
    events = data["events"]
    calendar = pd.DataFrame({"date": close.index})
    matched = _match(calendar, events, CONFIG["match_rule"])
    tone = matched["value"].rolling(20, min_periods=1).mean()
    signal = pd.Series(tone.clip(-1.0, 1.0).to_numpy(), index=close.index)
    positions = signal.shift(1)
    return positions
