import numpy as np
import pandas as pd
import pytest

from leakseed.data import make_data, perturb
from leakseed.oracle import OracleError, check
from leakseed.templates import CLASSES, render_case

N = 400


@pytest.fixture(scope="module")
def data():
    return make_data(N, seed=3)


def _compile(src: str):
    namespace: dict = {}
    exec(compile(src, "<case>", "exec"), namespace)
    return namespace["run"]


@pytest.mark.parametrize("cls", list(CLASSES))
def test_each_class_leaky_and_clean_function(cls, data):
    variant, lib = CLASSES[cls].combos[0]
    case = (cls, variant, lib, "L0")
    leaky = _compile(render_case(0, case, leak=True)[0])
    clean = _compile(render_case(0, case, leak=False)[0])
    assert check(leaky, data, seed=1)[0] == "leak"
    assert check(clean, data, seed=1)[0] == "clean"


def test_held_positions_need_a_one_bar_lag(data):
    def unlagged(d):
        return np.sign(d["close"].pct_change(fill_method=None))

    def lagged(d):
        return unlagged(d).shift(1)

    verdict, witness, _ = check(unlagged, data, seed=0)
    assert verdict == "leak" and witness["row"] == witness["t"] + 1
    assert check(lagged, data, seed=0)[0] == "clean"


def _late_peek(d):
    # Row 100 reads row 150; every other row is causal.
    close = d["close"].to_numpy()
    out = np.vstack([np.full((1, close.shape[1]), np.nan), close[:-1]])
    out[100] = close[150]
    return out


def test_leak_visible_only_for_some_t_needs_several_cuts(data):
    assert check(_late_peek, data, ts=[50])[0] == "clean"
    assert check(_late_peek, data, ts=[300])[0] == "clean"
    verdict, witness, _ = check(_late_peek, data, ts=[50, 120, 300])
    assert verdict == "leak" and witness["t"] == 120 and witness["row"] == 100
    # The stratified default grid is dense enough to land in [99, 149].
    assert check(_late_peek, data, seed=5)[0] == "leak"


def test_cuts_start_where_the_output_starts(data):
    # Output exists only in the last 40 rows and reads the last row of the sample. A cut before
    # those rows compares missing values, so it can never show this leak.
    def late_output(d):
        out = np.full(d["close"].shape, np.nan)
        out[-40:] = d["close"].to_numpy()[-1]
        return out

    assert check(late_output, data, n_t=1, seed=0, modes=("values",))[0] == "leak"


def test_availability_leak_needs_the_availability_mode(data):
    def survivors(d):
        close = d["close"]
        alive = close.iloc[-1].notna()
        signal = close.pct_change(fill_method=None).loc[:, alive].reindex(columns=close.columns)
        return signal.shift(1)

    assert check(survivors, data, modes=("values",), seed=0)[0] == "clean"
    assert check(survivors, data, modes=("availability",), seed=0)[0] == "leak"


def test_point_in_time_perturbation_respects_filing_dates(data):
    t = 200
    cut = data["close"].index[t]
    out = perturb(data, t, "values", np.random.default_rng(0))
    old, new = data["fundamentals"], out["fundamentals"]
    known = old["filed"] <= cut
    assert old.loc[known, "value"].equals(new.loc[known, "value"])
    assert not np.allclose(old.loc[~known, "value"], new.loc[~known, "value"])
    pd.testing.assert_frame_equal(data["close"].iloc[: t + 1], out["close"].iloc[: t + 1])


def test_events_of_day_t_are_known_at_its_close(data):
    def same_day(d):
        events = d["events"]
        daily = events.groupby(events["ts"].dt.normalize())["value"].mean()
        return np.sign(daily.reindex(d["close"].index).fillna(0.0)).shift(1)

    def next_day(d):
        return same_day(d).shift(-1)

    assert check(same_day, data, seed=1)[0] == "clean"
    assert check(next_day, data, seed=1)[0] == "leak"


def test_refuses_nondeterministic_vacuous_and_misshapen_outputs(data):
    rng = np.random.default_rng(0)
    with pytest.raises(OracleError, match="differs between two runs"):
        check(lambda d: rng.normal(size=len(d["close"])), data)
    with pytest.raises(OracleError, match="vacuous"):
        check(lambda d: np.ones(len(d["close"])), data)
    with pytest.raises(OracleError, match="one row per date"):
        check(lambda d: d["close"].to_numpy()[:-1], data)
    with pytest.raises(OracleError, match="columns"):
        check(lambda d: d["close"].iloc[:, :2].shift(1), data)
    with pytest.raises(OracleError, match="no finite"):
        check(lambda d: np.full(len(d["close"]), np.nan), data)
