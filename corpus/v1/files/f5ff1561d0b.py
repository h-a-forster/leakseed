import json

import pandas as pd

CONFIG = json.loads('{"side": "nearest"}')


def _attach_events(calendar, events, side):
    matched = pd.merge_asof(calendar, events, left_on="date", right_on="ts", direction=side)
    return matched


def run(data):
    close = data["close"]
    events = data["events"]
    calendar = pd.DataFrame({"date": close.index})
    matched = _attach_events(calendar, events, CONFIG["side"])
    tone = matched["value"].rolling(20, min_periods=1).mean()
    signal = pd.Series(tone.clip(-1.0, 1.0).to_numpy(), index=close.index)
    positions = signal.shift(1)
    return positions
