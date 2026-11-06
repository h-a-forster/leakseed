import polars as pl


def run(data):
    frame = pl.from_pandas(data["close"].reset_index())
    assets = [c for c in frame.columns if c != "date"]
    panel = frame.unpivot(index="date", on=assets, variable_name="asset", value_name="close").sort("asset", "date")
    panel = panel.with_columns(pl.col("close").pct_change().over("asset").alias("ret"))
    scored = panel.with_columns((pl.col("ret") - (pl.col("ret").cum_sum() / pl.col("ret").cum_count()).over("asset")).alias("excess"))
    wide = scored.pivot(on="asset", index="date", values="excess").sort("date")
    signal = wide.select(pl.col(assets).rolling_mean(40) * -100.0)
    positions = signal.select(pl.all().shift(1))
    return positions.to_numpy()
