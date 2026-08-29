import numpy as np
import pytest

from ml.anomaly.models import (
    AutoencoderDetector,
    IsolationForestDetector,
    OneClassSVMDetector,
    StatisticalThresholdDetector,
)


@pytest.fixture
def dummy_data():
    np.random.seed(42)
    # Generate 100 samples of normal data (mean 0, std 1) across 5 features
    normal_data = np.random.normal(loc=0.0, scale=1.0, size=(100, 5))

    # Generate 5 highly anomalous samples (outliers)
    anomalous_data = np.random.normal(loc=15.0, scale=2.0, size=(5, 5))
    return normal_data, anomalous_data


def test_statistical_detector(dummy_data):
    normal, anomalous = dummy_data
    detector = StatisticalThresholdDetector()
    detector.fit(normal)

    normal_scores = detector.predict_score(normal)
    anomalous_scores = detector.predict_score(anomalous)

    # Anomalous scores should be significantly higher than normal scores
    assert np.mean(anomalous_scores) > np.mean(normal_scores)

    # Details check
    scores, probs, severities = detector.predict_details(anomalous)
    assert len(scores) == 5
    assert (probs >= 0.0).all() and (probs <= 1.0).all()
    # Outliers with loc=15 should be flagged as HIGH or CRITICAL severity
    assert any(sev in ["HIGH", "CRITICAL"] for sev in severities)


def test_isolation_forest_detector(dummy_data):
    normal, anomalous = dummy_data
    detector = IsolationForestDetector(n_estimators=50, random_state=42)
    detector.fit(normal)

    normal_scores = detector.predict_score(normal)
    anomalous_scores = detector.predict_score(anomalous)

    assert np.mean(anomalous_scores) > np.mean(normal_scores)


def test_one_class_svm_detector(dummy_data):
    normal, anomalous = dummy_data
    detector = OneClassSVMDetector(nu=0.1)
    detector.fit(normal)

    normal_scores = detector.predict_score(normal)
    anomalous_scores = detector.predict_score(anomalous)

    assert np.mean(anomalous_scores) > np.mean(normal_scores)


def test_autoencoder_detector(dummy_data):
    normal, anomalous = dummy_data
    # Use small epoch size for fast testing
    detector = AutoencoderDetector(encoding_dim=3, epochs=2, batch_size=10, lr=0.01)
    detector.fit(normal)

    normal_scores = detector.predict_score(normal)
    anomalous_scores = detector.predict_score(anomalous)

    # Unsupervised reconstruction error should be larger for unseen anomalous data
    assert np.mean(anomalous_scores) > np.mean(normal_scores)
