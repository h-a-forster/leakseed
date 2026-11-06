import numpy as np
import pytest

from leakseed.data import make_data
from leakseed.impact import sharpe
from leakseed.oracle import as_matrix


def test_sharpe_on_a_hand_computed_case():
    close = np.array([[100.0], [110.0], [99.0], [108.9]])  # returns +10%, -10%, +10%
    assert sharpe(np.zeros((4, 1)), close) == 0.0  # flat: no variance in the pnl
    positions = np.array([[0.0], [1.0], [1.0], [1.0]])
    pnl = np.array([0.1, -0.1, 0.1])
    assert sharpe(positions, close) == pytest.approx(pnl.mean() / pnl.std() * np.sqrt(252))


def test_missing_positions_and_prices_are_flat_and_one_column_is_held_everywhere():
    close = np.array([[100.0, 100.0], [110.0, np.nan], [99.0, np.nan], [108.9, np.nan]])
    positions = np.array([[np.nan], [1.0], [1.0], [np.inf]])
    pnl = np.array([0.05, -0.05, 0.0])
    assert sharpe(positions, close) == pytest.approx(pnl.mean() / pnl.std() * np.sqrt(252))


def test_a_same_bar_position_shows_up_and_a_lagged_one_does_not():
    data = make_data(2000, 3)
    close = data["close"]
    returns = close.pct_change(fill_method=None)
    signal = np.sign(returns.rolling(10).mean())
    dates = close.index
    assert abs(sharpe(as_matrix(signal, dates), close.to_numpy())) > 2.0
    assert abs(sharpe(as_matrix(signal.shift(1), dates), close.to_numpy())) < 1.0
