import numpy as np
import pytest

from ml.classification.models import FailureThreatClassifier, FailureTypeClassifier


@pytest.fixture
def dummy_data():
    np.random.seed(42)
    # 100 samples, 10 features
    X = np.random.normal(size=(100, 10))
    # Binary targets: mostly 0, some 1
    y_bin = np.random.binomial(n=1, p=0.2, size=100)
    # Multi-class targets (failure modes)
    y_mc = np.random.choice(["None", "Bearing Failure", "Overheating"], size=100)
    return X, y_bin, y_mc


def test_failure_threat_classifier(dummy_data):
    X, y_bin, _ = dummy_data
    clf = FailureThreatClassifier(model_type="random_forest", random_state=42)
    clf.fit(X, y_bin)

    # Check predictions
    probs = clf.predict_proba(X)
    assert len(probs) == 100
    assert (probs >= 0.0).all() and (probs <= 1.0).all()

    preds = clf.predict(X)
    assert len(preds) == 100
    assert set(preds).issubset({0, 1})

    # Cost sensitive tuning
    opt_t = clf.tune_threshold_cost_sensitive(X, y_bin)
    assert 0.0 < opt_t < 1.0
    assert clf.optimal_threshold == opt_t


def test_failure_type_classifier(dummy_data):
    X, _, y_mc = dummy_data
    clf = FailureTypeClassifier(model_type="random_forest", random_state=42)
    clf.fit(X, y_mc)

    preds = clf.predict(X)
    assert len(preds) == 100
    assert set(preds).issubset({"None", "Bearing Failure", "Overheating"})

    probs = clf.predict_proba(X)
    assert probs.shape == (100, 3)
    assert np.allclose(np.sum(probs, axis=1), 1.0)
