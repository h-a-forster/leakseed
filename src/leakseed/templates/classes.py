"""The leak classes. Each function renders one (variant, library) program for a context.

Every script follows one contract: ``run(data)`` returns the positions *held over* each bar,
so row ``j`` may use data up to row ``j - 1``. A decision taken at the close of bar ``t`` uses
data up to ``t`` and is held over ``t + 1``; the scripts end with that one-bar lag.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .core import Ctx, Program, mode_site, param_site

NP = "import numpy as np"
PD = "import pandas as pd"
PL = "import polars as pl"


# Shared fragments ---------------------------------------------------------------------------


def _pd_close(p: Program, returns: bool = True) -> None:
    p.add('close = data["close"]')
    if returns:
        p.add("returns = close.pct_change(fill_method=None)")


def _pd_end(p: Program, signal: str = "signal") -> None:
    p.add(f"positions = {signal}.shift(1)\nreturn positions")


def _np_close(p: Program) -> None:
    p.need(NP)
    p.add(
        'close = data["close"].to_numpy()\n'
        "returns = np.full_like(close, np.nan)\n"
        "returns[1:] = close[1:] / close[:-1] - 1.0"
    )


def _np_momentum(p: Program, window: int) -> None:
    p.add(
        "csum = np.cumsum(np.nan_to_num(returns), axis=0)\n"
        "momentum = np.full_like(csum, np.nan)\n"
        f"momentum[{window}:] = (csum[{window}:] - csum[:-{window}]) / {window}"
    )


def _np_end(p: Program) -> None:
    p.add("positions = np.full_like(signal, np.nan)\npositions[1:] = signal[:-1]\nreturn positions")


def _pl_frame(p: Program, key: str = "close", name: str = "frame", assets: bool = True) -> None:
    p.need(PL)
    p.add(f'{name} = pl.from_pandas(data["{key}"].reset_index())')
    if assets:
        p.add(f'assets = [c for c in {name}.columns if c != "date"]')


def _pl_end(p: Program) -> None:
    p.add("positions = signal.select(pl.all().shift(1))\nreturn positions.to_numpy()")


# 1. Same-bar execution: the decision is not lagged before it is held. ------------------------


def same_bar(ctx: Ctx) -> Program:
    p = Program()
    w = ctx.pick((10, 20, 40))
    helper = ctx.pick(("to_positions", "hold", "execute"))
    name = ctx.pick(("delay", "lag", "execution_lag"))
    if ctx.lib == "pandas":
        p.need(NP)
        _pd_close(p, returns=ctx.variant == "a")
        if ctx.variant == "a":
            p.add(f"signal = np.sign(returns.rolling({w}).mean())")
        else:
            p.add(f"signal = -np.sign(close / close.rolling({w}).mean() - 1.0)")
        param_site(
            p, ctx, out="positions", args=["signal"], code="positions = signal.shift({v})",
            name=name, leak=0, clean=1, helper=helper,
            l0=("positions = signal", "positions = signal.shift(1)"),
        )  # fmt: skip
        p.add("return positions")
    elif ctx.lib == "numpy":
        _np_close(p)
        _np_momentum(p, w)
        if ctx.variant == "a":
            p.add("signal = np.sign(momentum)")
        else:
            p.add("signal = -np.clip(momentum * 100.0, -1.0, 1.0)")
        block = "positions = np.full_like(signal, np.nan)\npositions[{v}:] = signal[: len(signal) - {v}]"
        param_site(
            p, ctx, out="positions", args=["signal"], code=block, name=name, leak=0, clean=1,
            helper=helper,
            l0=("positions = signal.copy()", block.replace("{v}", "1")),
        )  # fmt: skip
        p.add("return positions")
    else:
        _pl_frame(p)
        p.add(f"signal = frame.select(pl.col(assets).pct_change().rolling_mean({w}).sign())")
        param_site(
            p, ctx, out="positions", args=["signal"],
            code="positions = signal.select(pl.all().shift({v}))", name=name, leak=0, clean=1,
            helper=helper,
            l0=("positions = signal", "positions = signal.select(pl.all().shift(1))"),
        )  # fmt: skip
        p.add("return positions.to_numpy()")
    return p


# 2. A negative shift (a lead) used as a feature. ---------------------------------------------


def negative_shift(ctx: Ctx) -> Program:
    p = Program()
    w = ctx.pick((10, 20, 40))
    k = ctx.pick((1, 2, 3, 5))
    helper = ctx.pick(("lagged", "offset", "align_feature"))
    name = ctx.pick(("periods", "horizon", "lag"))
    if ctx.lib == "pandas":
        p.need(NP)
        if ctx.variant == "a":
            _pd_close(p)
            param_site(
                p, ctx, out="feature", args=["returns"], code="feature = returns.shift({v})",
                name=name, leak=-k, clean=k, helper=helper,
            )  # fmt: skip
        else:
            _pd_close(p, returns=False)
            param_site(
                p, ctx, out="feature", args=["close"],
                code="feature = close.pct_change(periods={v}, fill_method=None)",
                name=name, leak=-k, clean=k, helper=helper,
            )  # fmt: skip
        p.add(f"signal = np.sign(feature.rolling({w}).mean())")
        _pd_end(p)
    else:
        _pl_frame(p)
        param_site(
            p, ctx, out="feature", args=["frame", "assets"],
            code="feature = frame.select(pl.col(assets).pct_change().shift({v}))",
            name=name, leak=-k, clean=k, helper=helper,
        )  # fmt: skip
        p.add(f"signal = feature.select(pl.all().rolling_mean({w}).sign())")
        _pl_end(p)
    return p


# 3. A centred rolling window. ----------------------------------------------------------------


def centered_rolling(ctx: Ctx) -> Program:
    p = Program()
    w = ctx.pick((5, 11, 21))
    helper = ctx.pick(("smooth", "window_stat", "rolling_view"))
    name = ctx.pick(("center", "centered", "symmetric"))
    if ctx.lib == "pandas":
        p.need(NP)
        if ctx.variant == "a":
            _pd_close(p, returns=False)
            param_site(
                p, ctx, out="smooth", args=["close"],
                code=f"smooth = close.rolling({w}, center={{v}}).mean()",
                name=name, leak=True, clean=False, helper=helper,
            )  # fmt: skip
            p.add("signal = np.sign(close - smooth)")
        else:
            _pd_close(p)
            param_site(
                p, ctx, out="vol", args=["returns"],
                code=f"vol = returns.rolling({w}, center={{v}}).std()",
                name=name, leak=True, clean=False, helper=helper,
            )  # fmt: skip
            p.add("signal = np.sign(returns.rolling(5).mean()) * 0.01 / vol")
        _pd_end(p)
    else:
        _pl_frame(p)
        if ctx.variant == "a":
            expr = f"(pl.col(c) - pl.col(c).rolling_mean({w}, center={{v}})).sign()"
        else:
            expr = f"(0.01 / pl.col(c).pct_change().rolling_std({w}, center={{v}})).alias(c)"
        param_site(
            p, ctx, out="signal", args=["frame", "assets"],
            code=f"signal = frame.select([{expr} for c in assets])",
            name=name, leak=True, clean=False, helper=helper,
        )  # fmt: skip
        _pl_end(p)
    return p


# 4. A scaler or z-score fitted on the full sample. -------------------------------------------


def full_sample_scaling(ctx: Ctx) -> Program:
    p = Program()
    w = ctx.pick((10, 20, 40))
    helper = ctx.pick(("standardise", "normalise", "score"))
    name = ctx.pick(("stat_window", "scaling", "fit_span"))
    alias = ctx.pick(("raw", "x", "values"))
    if ctx.lib == "pandas":
        _pd_close(p)
        p.add(f"momentum = returns.rolling({w}).mean()")
        mode_site(
            p, ctx, out="score", args=["momentum"],
            leak_code="score = (momentum - momentum.mean()) / momentum.std()",
            clean_code=(
                "score = (momentum - momentum.expanding().mean()) / momentum.expanding().std()"
            ),
            name=name, modes=("full", "expanding"), helper=helper, alias=alias,
        )  # fmt: skip
        p.add("signal = score.clip(-2.0, 2.0)")
        _pd_end(p)
    elif ctx.lib == "numpy" and ctx.variant == "a":
        _np_close(p)
        p.add("level = np.log(close)")
        mode_site(
            p, ctx, out="score", args=["level"],
            leak_code="score = level - np.nanmean(level, axis=0)",
            clean_code=(
                "score = level - np.nancumsum(level, axis=0) / np.cumsum(~np.isnan(level), axis=0)"
            ),
            name=name, modes=("full", "expanding"), helper=helper, alias=alias,
        )  # fmt: skip
        p.add("signal = -np.clip(score * 5.0, -1.0, 1.0)")
        _np_end(p)
    elif ctx.lib == "numpy":
        p.need("from sklearn.preprocessing import StandardScaler")
        _np_close(p)
        p.add("features = np.nan_to_num(returns)\ntrain_end = len(features) // 2")
        param_site(
            p, ctx, out="scaler", args=["features"],
            code="scaler = StandardScaler().fit(features[: int(len(features) * {v})])",
            name=ctx.pick(("fit_fraction", "train_share", "in_sample")), leak=1.0, clean=0.5,
            helper=helper,
        )  # fmt: skip
        p.add(
            "signal = -np.clip(scaler.transform(features), -2.0, 2.0)\nsignal[:train_end] = np.nan"
        )
        _np_end(p)
    else:
        _pl_frame(p)
        p.add(f"momentum = frame.select(pl.col(assets).pct_change().rolling_mean({w}))")
        mode_site(
            p, ctx, out="score", args=["momentum"],
            leak_code="score = momentum.select(pl.all() - pl.all().mean())",
            clean_code="score = momentum.select(pl.all() - pl.all().cum_sum() / pl.all().cum_count())",
            name=name, modes=("full", "expanding"), helper=helper, alias=alias,
        )  # fmt: skip
        p.add("signal = score.select((pl.all() * 100.0).clip(-1.0, 1.0))")
        _pl_end(p)
    return p


# 5. Backward fill or interpolation across time. ----------------------------------------------


def backfill_interpolate(ctx: Ctx) -> Program:
    p = Program()
    w = ctx.pick((10, 20, 40))
    helper = ctx.pick(("fill_gaps", "repair", "impute"))
    name = ctx.pick(("fill", "strategy", "gap_rule"))
    alias = ctx.pick(("raw", "vol_in", "series"))
    if ctx.lib == "pandas":
        p.need(NP)
        _pd_close(p)
        p.add('volume = data["volume"]')
        if ctx.variant == "a":
            leak_code, modes = "filled = volume.bfill()", ("backward", "forward")
        else:
            leak_code, modes = "filled = volume.interpolate()", ("linear", "pad")
        mode_site(
            p, ctx, out="filled", args=["volume"], leak_code=leak_code,
            clean_code="filled = volume.ffill()", name=name, modes=modes, helper=helper,
            alias=alias,
        )  # fmt: skip
        p.add(f"surge = filled / filled.rolling({w}).mean() - 1.0")
        p.add("signal = np.sign(returns) * surge.clip(-1.0, 1.0)")
        _pd_end(p)
    else:
        _pl_frame(p)
        _pl_frame(p, key="volume", name="volume", assets=False)
        if ctx.variant == "a":
            param_site(
                p, ctx, out="filled", args=["volume", "assets"],
                code="filled = volume.select(pl.col(assets).fill_null(strategy={v}))",
                name=name, leak="backward", clean="forward", helper=helper,
            )  # fmt: skip
        else:
            mode_site(
                p, ctx, out="filled", args=["volume", "assets"],
                leak_code="filled = volume.select(pl.col(assets).interpolate())",
                clean_code='filled = volume.select(pl.col(assets).fill_null(strategy="forward"))',
                name=name, modes=("linear", "forward"), helper=helper, alias=alias,
            )  # fmt: skip
        p.add(f"surge = filled.select(pl.all() / pl.all().rolling_mean({w}) - 1.0)")
        p.add(
            "signal = pl.DataFrame([frame[c].pct_change().sign() * surge[c].clip(-1.0, 1.0)"
            " for c in assets])"
        )
        _pl_end(p)
    return p


# 6. Resampling with a label (or closed side) that stamps a bin before it ends. ---------------


def resample_label(ctx: Ctx) -> Program:
    p = Program()
    helper = ctx.pick(("weekly", "to_weeks", "bin_weeks"))
    name = ctx.pick(("label", "stamp", "bin_label"))
    if ctx.lib == "pandas":
        p.need(NP)
        if ctx.variant == "a":
            _pd_close(p, returns=False)
            param_site(
                p, ctx, out="weekly", args=["close"],
                code='weekly = close.resample("W-FRI", label={v}, closed="right").last()',
                name=name, leak="left", clean="right", helper=helper,
            )  # fmt: skip
            p.add(
                'daily = weekly.pct_change(fill_method=None).reindex(close.index, method="ffill")'
            )
            p.add("signal = np.sign(daily)")
        else:
            _pd_close(p)
            p.add('volume = data["volume"]')
            param_site(
                p, ctx, out="weekly", args=["volume"],
                code='weekly = volume.resample("W-FRI", label={v}, closed="left").mean()',
                name=name, leak="left", clean="right", helper=helper,
            )  # fmt: skip
            p.add('daily = weekly.reindex(volume.index, method="ffill")')
            p.add("surge = volume.ffill() / daily - 1.0")
            p.add("signal = np.sign(returns) * surge.clip(-1.0, 1.0)")
        _pd_end(p)
    else:
        _pl_frame(p)
        param_site(
            p, ctx, out="weekly", args=["frame", "assets"],
            code=(
                'weekly = frame.group_by_dynamic("date", every="1w", label={v}, closed="left")'
                ".agg(pl.col(assets).last())"
            ),
            name=name, leak="left", clean="right", helper=helper,
        )  # fmt: skip
        p.add("weekly = weekly.with_columns(pl.col(assets).pct_change())")
        p.add('daily = frame.select("date").join_asof(weekly, on="date", strategy="backward")')
        p.add("signal = daily.select(pl.col(assets).sign())")
        _pl_end(p)
    return p


# 7. An as-of join that looks forward. --------------------------------------------------------


def asof_forward(ctx: Ctx) -> Program:
    p = Program()
    w = ctx.pick((5, 10, 20))
    helper = ctx.pick(("attach_events", "align_events", "match"))
    name = ctx.pick(("direction", "match_rule", "side"))
    leak = "forward" if ctx.variant == "a" else "nearest"
    if ctx.lib == "pandas":
        p.need(PD)
        _pd_close(p, returns=False)
        p.add('events = data["events"]\ncalendar = pd.DataFrame({"date": close.index})')
        param_site(
            p, ctx, out="matched", args=["calendar", "events"],
            code='matched = pd.merge_asof(calendar, events, left_on="date", right_on="ts", direction={v})',
            name=name, leak=leak, clean="backward", helper=helper,
        )  # fmt: skip
        p.add(f'tone = matched["value"].rolling({w}, min_periods=1).mean()')
        p.add("signal = pd.Series(tone.clip(-1.0, 1.0).to_numpy(), index=close.index)")
        _pd_end(p)
    else:
        p.need(PL)
        p.add('calendar = pl.from_pandas(data["close"].reset_index()).select("date")')
        p.add('events = pl.from_pandas(data["events"])')
        param_site(
            p, ctx, out="matched", args=["calendar", "events"],
            code='matched = calendar.join_asof(events, left_on="date", right_on="ts", strategy={v})',
            name=name, leak=leak, clean="backward", helper=helper,
        )  # fmt: skip
        p.add(
            f'signal = matched.select(pl.col("value").rolling_mean({w}, min_samples=1).clip(-1.0, 1.0))'
        )
        _pl_end(p)
    return p


# 8. Fundamentals placed at the period end instead of the filing date. ------------------------


def fundamentals_period_end(ctx: Ctx) -> Program:
    p = Program()
    helper = ctx.pick(("as_table", "place", "align_filings"))
    name = ctx.pick(("key", "time_column", "stamp"))
    if ctx.lib == "pandas":
        _pd_close(p, returns=False)
        p.add('fundamentals = data["fundamentals"]')
        if ctx.variant == "a":
            param_site(
                p, ctx, out="table", args=["fundamentals"],
                code='table = fundamentals.pivot_table(index={v}, columns="asset", values="value")',
                name=name, leak="period_end", clean="filed", helper=helper,
            )  # fmt: skip
            p.add("table = table.reindex(columns=close.columns)")
            p.add(
                "known = table.reindex(table.index.union(close.index)).ffill().reindex(close.index)"
            )
        else:
            p.add(
                'grid = close.stack().rename("close").reset_index().astype({"asset": object})\n'
                'grid = grid.sort_values("date")'
            )
            param_site(
                p, ctx, out="matched", args=["grid", "fundamentals"],
                code=(
                    "book = fundamentals.sort_values({v})\n"
                    'matched = pd.merge_asof(grid, book, left_on="date", right_on={v}, by="asset")'
                ),
                name=name, leak="period_end", clean="filed", helper=helper,
            )  # fmt: skip
            p.need(PD)
            p.add(
                'known = matched.pivot_table(index="date", columns="asset", values="value")\n'
                "known = known.reindex(index=close.index, columns=close.columns)"
            )
        p.add("signal = known.rank(axis=1, pct=True) - 0.5")
        _pd_end(p)
    else:
        p.need(PL)
        p.add('assets = list(data["close"].columns)')
        p.add('calendar = pl.from_pandas(data["close"].reset_index()).select("date")')
        p.add('fundamentals = pl.from_pandas(data["fundamentals"])')
        param_site(
            p, ctx, out="known", args=["calendar", "fundamentals"],
            code=(
                'table = fundamentals.pivot(on="asset", index={v}, values="value", '
                'aggregate_function="mean").sort({v})\n'
                'known = calendar.join_asof(table, left_on="date", right_on={v}, strategy="backward")'
            ),
            name=name, leak="period_end", clean="filed", helper=helper,
        )  # fmt: skip
        p.add("signal = known.select([pl.col(c) - pl.mean_horizontal(assets) for c in assets])")
        _pl_end(p)
    return p


# 9. A restated value overwriting the value first reported. -----------------------------------


def restatement_overwrite(ctx: Ctx) -> Program:
    p = Program()
    helper = ctx.pick(("collapse", "pick_version", "dedupe"))
    name = ctx.pick(("version", "keep", "which"))
    _pd_close(p, returns=False)
    p.add('pit = data["fundamentals_pit"].sort_values("filed")')
    if ctx.variant == "a":
        param_site(
            p, ctx, out="latest", args=["pit"],
            code=(
                'latest = pit.groupby(["asset", "period_end"], as_index=False).agg('
                'value=("value", {v}), filed=("filed", "first"))'
            ),
            name=name, leak="last", clean="first", helper=helper,
        )  # fmt: skip
    else:
        param_site(
            p, ctx, out="latest", args=["pit"],
            code=(
                'chosen = pit.groupby(["asset", "period_end"])["value"].transform({v})\n'
                'latest = pit.assign(value=chosen).drop_duplicates(["asset", "period_end"])'
            ),
            name=name, leak="last", clean="first", helper=helper,
        )  # fmt: skip
    p.add(
        'table = latest.pivot_table(index="filed", columns="asset", values="value")\n'
        "table = table.reindex(columns=close.columns)\n"
        "known = table.reindex(table.index.union(close.index)).ffill().reindex(close.index)\n"
        "signal = known.rank(axis=1, pct=True) - 0.5"
    )
    _pd_end(p)
    return p


# 10. Survivorship: a universe chosen with knowledge of the end of the sample. ----------------


def survivorship(ctx: Ctx) -> Program:
    p = Program()
    w = ctx.pick((20, 60, 120))
    helper = ctx.pick(("universe", "eligible", "filter_names"))
    name = ctx.pick(("membership_rule", "universe_rule", "screen"))
    alias = ctx.pick(("scores", "ranked", "candidates"))
    _pd_close(p)
    p.add(f"raw = returns.rolling({w}).mean().rank(axis=1, pct=True) - 0.5")
    if ctx.variant == "a":
        p.add('membership = data["membership"]')
        leak = "signal = raw.loc[:, membership.iloc[-1]].reindex(columns=raw.columns)"
        clean = "signal = raw.where(membership)"
        other = "membership"
    else:
        leak = "signal = raw.loc[:, close.iloc[-1].notna()].reindex(columns=raw.columns)"
        clean = "signal = raw.where(close.notna())"
        other = "close"
    mode_site(
        p, ctx, out="signal", args=["raw", other], leak_code=leak, clean_code=clean, name=name,
        modes=("final", "as_of"), helper=helper, alias=alias,
    )  # fmt: skip
    _pd_end(p)
    return p


# 11. A shuffled split or K-fold on a time series. --------------------------------------------


def shuffled_split(ctx: Ctx) -> Program:
    p = Program()
    helper = ctx.pick(("split_rows", "partition", "make_folds"))
    if ctx.lib == "pandas":
        p.need(NP, PD, "from sklearn.model_selection import train_test_split")
        _pd_close(p)
        p.add(
            "market = returns.mean(axis=1)\n"
            "lags = pd.concat({k: market.shift(k) for k in (1, 2, 3)}, axis=1)\n"
            "now = pd.concat({k: market.shift(k - 1) for k in (1, 2, 3)}, axis=1)\n"
            "rows = np.flatnonzero(lags.notna().all(axis=1).to_numpy())"
        )
        param_site(
            p, ctx, out="train, test", args=["rows"],
            code="train, test = train_test_split(rows, test_size=0.3, shuffle={v}, random_state=0)",
            name=ctx.pick(("shuffle", "randomise", "mix")), leak=True, clean=False,
            helper=helper,
            l0=(
                "train, test = train_test_split(rows, test_size=0.3, random_state=0)",
                "train, test = train_test_split(rows, test_size=0.3, shuffle=False, random_state=0)",
            ),
        )  # fmt: skip
        p.add(
            "coef, *_ = np.linalg.lstsq(lags.to_numpy()[train], market.to_numpy()[train], rcond=None)\n"
            "forecast = now.to_numpy() @ coef\n"
            "signal = pd.Series(np.nan, index=close.index)\n"
            "signal.iloc[test] = forecast[test]"
        )
        _pd_end(p)
    else:
        _np_close(p)
        p.add(
            "n = len(close)\n"
            "market = np.zeros(n)\n"
            "market[1:] = np.nanmean(returns[1:], axis=1)\n"
            "lags = np.full((n, 3), np.nan)\n"
            "now = np.full((n, 3), np.nan)\n"
            "for k in (1, 2, 3):\n"
            "    lags[k:, k - 1] = market[:-k]\n"
            "    now[k - 1 :, k - 1] = market[: n - k + 1]\n"
            "rows = np.arange(3, n)"
        )
        mode_site(
            p, ctx, out="folds", args=["rows"],
            leak_code="folds = list(KFold(n_splits=5).split(rows))",
            clean_code="folds = list(TimeSeriesSplit(n_splits=5).split(rows))",
            name=ctx.pick(("scheme", "cv", "folds_kind")), modes=("kfold", "walk_forward"),
            helper=helper, alias=ctx.pick(("index", "idx", "positions_idx")),
            leak_imports=("from sklearn.model_selection import KFold",),
            clean_imports=("from sklearn.model_selection import TimeSeriesSplit",),
        )  # fmt: skip
        p.add(
            "signal = np.full(n, np.nan)\n"
            "for train, test in folds:\n"
            "    coef, *_ = np.linalg.lstsq(lags[rows[train]], market[rows[train]], rcond=None)\n"
            "    signal[rows[test]] = now[rows[test]] @ coef"
        )
        _np_end(p)
    return p


# 12. A group transform over the full history. ------------------------------------------------


def groupby_transform(ctx: Ctx) -> Program:
    p = Program()
    w = ctx.pick((10, 20, 40))
    helper = ctx.pick(("baseline", "group_mean", "normal_level"))
    name = ctx.pick(("history", "pooling", "mean_span"))
    alias = ctx.pick(("long", "tbl", "frame_long"))
    if ctx.lib == "pandas":
        _pd_close(p)
        p.add('panel = returns.stack().rename("ret").reset_index()')
        key = '"asset"' if ctx.variant == "a" else 'panel["date"].dt.month'
        mode_site(
            p, ctx, out="baseline", args=["panel"],
            leak_code=f'baseline = panel.groupby({key})["ret"].transform("mean")',
            clean_code=(
                f'baseline = panel.groupby({key})["ret"].transform(lambda s: s.expanding().mean())'
            ),
            name=name, modes=("full", "expanding"), helper=helper, alias=alias,
        )  # fmt: skip
        p.add(
            'excess = panel.assign(excess=panel["ret"] - baseline)\n'
            'wide = excess.pivot(index="date", columns="asset", values="excess")\n'
            "wide = wide.reindex(index=close.index, columns=close.columns)\n"
            f"signal = -wide.rolling({w}).mean() * 100.0"
        )
        _pd_end(p)
    else:
        _pl_frame(p)
        p.add(
            'panel = frame.unpivot(index="date", on=assets, variable_name="asset", '
            'value_name="close").sort("asset", "date")\n'
            'panel = panel.with_columns(pl.col("close").pct_change().over("asset").alias("ret"))'
        )
        mode_site(
            p, ctx, out="scored", args=["panel"],
            leak_code=(
                'scored = panel.with_columns((pl.col("ret") - pl.col("ret").mean().over("asset"))'
                '.alias("excess"))'
            ),
            clean_code=(
                'scored = panel.with_columns((pl.col("ret") - (pl.col("ret").cum_sum() '
                '/ pl.col("ret").cum_count()).over("asset")).alias("excess"))'
            ),
            name=name, modes=("full", "expanding"), helper=helper, alias=alias,
        )  # fmt: skip
        p.add(
            'wide = scored.pivot(on="asset", index="date", values="excess").sort("date")\n'
            f"signal = wide.select(pl.col(assets).rolling_mean({w}) * -100.0)"
        )
        _pl_end(p)
    return p


# 13. np.roll wraparound. ---------------------------------------------------------------------


def np_roll(ctx: Ctx) -> Program:
    p = Program()
    k = ctx.pick((1, 2, 5))
    w = ctx.pick((5, 10, 20))
    helper = ctx.pick(("lag_rows", "delayed", "past"))
    name = ctx.pick(("warmup", "pad", "burn_in"))
    _np_close(p)
    if ctx.variant == "a":
        p.add("filled = np.nan_to_num(returns)")
        block = f"lagged = np.roll(filled, {k}, axis=0)\nlagged[:{{v}}] = np.nan"
        param_site(
            p, ctx, out="lagged", args=["filled"], code=block, name=name, leak=0, clean=k,
            helper=helper,
            l0=(f"lagged = np.roll(filled, {k}, axis=0)", block.replace("{v}", str(k))),
        )  # fmt: skip
        p.add("signal = np.clip((filled - lagged) * 50.0, -1.0, 1.0)")
    else:
        block = (
            "total = np.zeros_like(returns)\n"
            f"for shift in range(1, {w + 1}):\n"
            "    total += np.roll(returns, shift, axis=0)\n"
            "total[:{v}] = np.nan"
        )
        l0_leak = "\n".join(block.splitlines()[:3])
        param_site(
            p, ctx, out="total", args=["returns"], code=block, name=name, leak=0, clean=w,
            helper=helper, l0=(l0_leak, block.replace("{v}", str(w))),
        )  # fmt: skip
        p.add(f"signal = np.sign(total / {w})")
    _np_end(p)
    return p


# 14. Reversed cumulative statistics. ---------------------------------------------------------


def reversed_cumulative(ctx: Ctx) -> Program:
    p = Program()
    helper = ctx.pick(("running_peak", "high_water", "envelope"))
    name = ctx.pick(("direction", "scan", "order"))
    alias = ctx.pick(("prices", "px", "level"))
    if ctx.lib == "pandas" and ctx.variant == "a":
        _pd_close(p, returns=False)
        mode_site(
            p, ctx, out="peak", args=["close"],
            leak_code="peak = close[::-1].cummax()[::-1]", clean_code="peak = close.cummax()",
            name=name, modes=("reverse", "forward"), helper=helper, alias=alias,
        )  # fmt: skip
        p.add("signal = (1.0 + 5.0 * (close / peak - 1.0)).clip(lower=0.0)")
        _pd_end(p)
    elif ctx.lib == "pandas":
        p.need(NP)
        _pd_close(p)
        p.add('volume = data["volume"]')
        mode_site(
            p, ctx, out="cumulative", args=["volume"],
            leak_code="cumulative = volume[::-1].cumsum()[::-1]",
            clean_code="cumulative = volume.cumsum()",
            name=name, modes=("reverse", "forward"), helper=helper, alias=alias,
        )  # fmt: skip
        p.add("signal = np.sign(returns) * (volume / cumulative * 100.0).clip(0.0, 1.0)")
        _pd_end(p)
    elif ctx.lib == "numpy":
        _np_close(p)
        mode_site(
            p, ctx, out="peak", args=["close"],
            leak_code="peak = np.fmax.accumulate(close[::-1], axis=0)[::-1]",
            clean_code="peak = np.fmax.accumulate(close, axis=0)",
            name=name, modes=("reverse", "forward"), helper=helper, alias=alias,
        )  # fmt: skip
        p.add("signal = np.clip(1.0 + 5.0 * (close / peak - 1.0), 0.0, None)")
        _np_end(p)
    else:
        _pl_frame(p)
        param_site(
            p, ctx, out="peak", args=["frame", "assets"],
            code="peak = frame.select(pl.col(assets).cum_max(reverse={v}))",
            name=name, leak=True, clean=False, helper=helper,
        )  # fmt: skip
        p.add(
            "signal = pl.DataFrame([(1.0 + 5.0 * (frame[c] / peak[c] - 1.0)).clip(0.0)"
            " for c in assets])"
        )
        _pl_end(p)
    return p


# 15. A parameter picked by argmax over the full sample. --------------------------------------


def argmax_param(ctx: Ctx) -> Program:
    p = Program()
    helper = ctx.pick(("selection_end", "fit_window", "tuning_cut"))
    name = ctx.pick(("tuning_share", "select_on", "fraction"))
    if ctx.lib == "pandas":
        p.need(NP)
        _pd_close(p)
        grid = ctx.pick(((5, 10, 20, 40), (3, 10, 30, 60), (5, 15, 30, 90)))
        p.add(
            "train_end = len(close) // 2\n"
            "candidates = {}\n"
            "pnls = {}\n"
            f"for window in {grid}:\n"
            "    candidates[window] = np.sign(returns.rolling(window).mean())\n"
            "    pnls[window] = (candidates[window].shift(1) * returns).mean(axis=1)"
        )
        param_site(
            p, ctx, out="cut", args=["close"], code="cut = int(len(close) * {v})", name=name,
            leak=1.0, clean=0.5, helper=helper,
        )  # fmt: skip
        p.add(
            "scores = {w: s.iloc[:cut].mean() / s.iloc[:cut].std() for w, s in pnls.items()}\n"
            "best = max(scores, key=scores.get)\n"
            "signal = candidates[best].copy()\n"
            "signal.iloc[:train_end] = np.nan"
        )
        _pd_end(p)
    else:
        w = ctx.pick((10, 20, 40))
        _np_close(p)
        _np_momentum(p, w)
        p.add("train_end = len(close) // 2")
        param_site(
            p, ctx, out="cut", args=["close"], code="cut = int(len(close) * {v})", name=name,
            leak=1.0, clean=0.5, helper=helper,
        )  # fmt: skip
        p.add(
            "grid = (0.0, 0.0005, 0.001, 0.002)\n"
            "sharpes = []\n"
            "for level in grid:\n"
            "    held = np.zeros_like(momentum)\n"
            "    held[1:] = np.where(np.abs(momentum[:-1]) > level, np.sign(momentum[:-1]), 0.0)\n"
            "    pnl = np.nan_to_num(held * returns).mean(axis=1)[:cut]\n"
            "    sharpes.append(pnl.mean() / pnl.std())\n"
            "best = grid[int(np.argmax(sharpes))]\n"
            "signal = np.where(np.abs(momentum) > best, np.sign(momentum), 0.0)\n"
            "signal[:train_end] = np.nan"
        )
        _np_end(p)
    return p


# Registry ------------------------------------------------------------------------------------


@dataclass(frozen=True)
class LeakClass:
    name: str
    description: str
    combos: tuple[tuple[str, str], ...]  # (variant, library)
    render: Callable[[Ctx], Program]


def _c(name, description, combos, render):
    return LeakClass(name, description, tuple(combos), render)


CLASSES: dict[str, LeakClass] = {
    c.name: c
    for c in (
        _c("same_bar", "decision held on the bar it was computed (no one-bar lag)",
           [("a", "pandas"), ("b", "pandas"), ("a", "numpy"), ("b", "numpy"), ("a", "polars")],
           same_bar),
        _c("negative_shift", "shift(-k) or pct_change(-k) used as a feature",
           [("a", "pandas"), ("b", "pandas"), ("a", "polars")], negative_shift),
        _c("centered_rolling", "rolling window with center=True",
           [("a", "pandas"), ("b", "pandas"), ("a", "polars"), ("b", "polars")],
           centered_rolling),
        _c("full_sample_scaling", "z-score, demeaning or scaler fitted on the full sample",
           [("a", "pandas"), ("a", "numpy"), ("b", "numpy"), ("a", "polars")],
           full_sample_scaling),
        _c("backfill_interpolate", "backward fill or interpolation across time",
           [("a", "pandas"), ("b", "pandas"), ("a", "polars"), ("b", "polars")],
           backfill_interpolate),
        _c("resample_label", "resampled bin stamped before it closes (label/closed misuse)",
           [("a", "pandas"), ("b", "pandas"), ("a", "polars")], resample_label),
        _c("asof_forward", "as-of join with direction forward or nearest",
           [("a", "pandas"), ("b", "pandas"), ("a", "polars")], asof_forward),
        _c("fundamentals_period_end", "fundamentals placed at period end, not filing date",
           [("a", "pandas"), ("b", "pandas"), ("a", "polars")], fundamentals_period_end),
        _c("restatement_overwrite", "restated value used from the first filing date",
           [("a", "pandas"), ("b", "pandas")], restatement_overwrite),
        _c("survivorship", "universe chosen by end-of-sample membership or listing",
           [("a", "pandas"), ("b", "pandas")], survivorship),
        _c("shuffled_split", "shuffled train_test_split or KFold on a time series",
           [("a", "pandas"), ("b", "numpy")], shuffled_split),
        _c("groupby_transform", "group transform('mean') over the full history",
           [("a", "pandas"), ("b", "pandas"), ("a", "polars")], groupby_transform),
        _c("np_roll", "np.roll wraparound brings the last rows to the front",
           [("a", "numpy"), ("b", "numpy")], np_roll),
        _c("reversed_cumulative", "cumulative statistic computed on the reversed series",
           [("a", "pandas"), ("b", "pandas"), ("a", "numpy"), ("a", "polars")],
           reversed_cumulative),
        _c("argmax_param", "parameter chosen by argmax of performance over the full sample",
           [("a", "pandas"), ("b", "numpy")], argmax_param),
    )
}  # fmt: skip
