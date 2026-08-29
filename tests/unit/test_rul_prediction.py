import numpy as np
import pytest

from ml.rul.models import LSTMRULRegressor, RandomForestRULRegressor


@pytest.fixture
def dummy_data():
    np.random.seed(42)
    # Tabular data: 100 samples, 10 features
    X_tab = np.random.normal(size=(100, 10))
    y_tab = np.linspace(160.0, 0.0, 100)  # Countdown RUL from 160 to 0

    # Sequence data: 50 sequences of length 6, 10 features
    X_seq = np.random.normal(size=(50, 6, 10))
    y_seq = np.linspace(120.0, 0.0, 50)

    return X_tab, y_tab, X_seq, y_seq


def test_random_forest_rul_regressor(dummy_data):
    X_tab, y_tab, _, _ = dummy_data
    reg = RandomForestRULRegressor(n_estimators=10, max_depth=5, random_state=42)
    reg.fit(X_tab, y_tab)

    mean, lower, upper = reg.predict_with_interval(X_tab)
    assert len(mean) == 100
    assert len(lower) == 100
    assert len(upper) == 100

    # Verify piecewise clipping is enforced (max RUL is 24)
    assert (mean <= 24.0).all()
    assert (lower <= mean).all()
    assert (mean <= upper).all()


def test_lstm_rul_regressor(dummy_data):
    _, _, X_seq, y_seq = dummy_data
    # Fit with small epochs for fast testing
    reg = LSTMRULRegressor(
        seq_length=6, hidden_dim=8, num_layers=1, epochs=2, batch_size=10, lr=0.01
    )
    reg.fit(X_seq, y_seq)

    mean, lower, upper = reg.predict_with_interval(X_seq)
    assert len(mean) == 50
    assert len(lower) == 50
    assert len(upper) == 50

    assert (mean <= 24.0).all()
    assert (lower <= mean).all()
    assert (mean <= upper).all()
