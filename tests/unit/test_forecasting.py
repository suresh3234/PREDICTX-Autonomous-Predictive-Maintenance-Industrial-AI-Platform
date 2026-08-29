import numpy as np
import pytest

from ml.forecasting.models import LSTMForecaster, RidgeForecaster


@pytest.fixture
def dummy_data():
    np.random.seed(42)
    # 100 samples, 10 features
    X_tab = np.random.normal(size=(100, 10))
    # 15 targets (5 sensors x 3 horizons)
    y = np.random.normal(size=(100, 15))

    # 50 sequences of length 6, 10 features
    X_seq = np.random.normal(size=(50, 6, 10))
    y_seq = np.random.normal(size=(50, 15))

    return X_tab, y, X_seq, y_seq


def test_ridge_forecaster(dummy_data):
    X_tab, y, _, _ = dummy_data
    forecaster = RidgeForecaster(alpha=1.0, random_state=42)
    forecaster.fit(X_tab, y)

    preds = forecaster.predict(X_tab)
    assert preds.shape == (100, 15)
    assert not np.isnan(preds).any()


def test_lstm_forecaster(dummy_data):
    _, _, X_seq, y_seq = dummy_data
    # Use small dimensions and epoch count for rapid testing
    forecaster = LSTMForecaster(
        seq_length=6, hidden_dim=8, num_layers=1, epochs=2, batch_size=10, lr=0.01
    )
    forecaster.fit(X_seq, y_seq)

    preds = forecaster.predict(X_seq)
    assert preds.shape == (50, 15)
    assert not np.isnan(preds).any()
