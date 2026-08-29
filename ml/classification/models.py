import numpy as np
from lightgbm import LGBMClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier


class FailureThreatClassifier:
    """
    Binary classifier wrapper designed to predict the probability of machine failure
    within the target degradation window (RUL <= 120 hours).

    Supports cost-sensitive threshold tuning to optimize business outcomes rather
    than blindly splitting at a default threshold of 0.5.
    """

    def __init__(self, model_type="xgboost", random_state=42, **kwargs):
        self.model_type = model_type
        self.random_state = random_state
        self.optimal_threshold = 0.5  # Default threshold

        # Initialize selected base estimator with class weighting
        if model_type == "logistic_regression":
            self.model = LogisticRegression(
                class_weight="balanced",
                random_state=random_state,
                max_iter=1000,
                **kwargs,
            )
        elif model_type == "random_forest":
            self.model = RandomForestClassifier(
                class_weight="balanced", random_state=random_state, **kwargs
            )
        elif model_type == "xgboost":
            # For XGBoost, scale_pos_weight is configured dynamically during fitting
            self.model = XGBClassifier(
                random_state=random_state, eval_metric="logloss", **kwargs
            )
        elif model_type == "lightgbm":
            self.model = LGBMClassifier(
                class_weight="balanced", random_state=random_state, verbose=-1, **kwargs
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")

    def fit(self, X: np.ndarray, y: np.ndarray):
        if self.model_type == "xgboost":
            # Compute class weights based on binary label balance
            num_neg = np.sum(y == 0)
            num_pos = np.sum(y == 1)
            scale_pos = max(1.0, num_neg / (num_pos + 1e-8))
            self.model.set_params(scale_pos_weight=scale_pos)

        self.model.fit(X, y)
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Returns the probability of the positive class (failure risk)."""
        probs = self.model.predict_proba(X)
        if probs.shape[1] == 1:
            known_class = self.model.classes_[0]
            if known_class == 0:
                return np.zeros(X.shape[0])
            else:
                return np.ones(X.shape[0])
        return probs[:, 1]

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predicts binary outcome based on the tuned optimal threshold."""
        probs = self.predict_proba(X)
        return (probs >= self.optimal_threshold).astype(int)

    def tune_threshold_cost_sensitive(
        self,
        X: np.ndarray,
        y: np.ndarray,
        cost_maintenance=150.0,
        cost_inspection=30.0,
        cost_downtime=1000.0,
    ) -> float:
        """
        Tunes the decision threshold on validation data to minimize the expected operational cost.

        Expected Cost Equation:
            Expected Cost = TP * cost_maintenance + FP * cost_inspection + FN * cost_downtime
        """
        probs = self.predict_proba(X)
        thresholds = np.linspace(0.01, 0.99, 99)
        best_threshold = 0.5
        min_cost = float("inf")

        for t in thresholds:
            preds = (probs >= t).astype(int)

            tp = np.sum((preds == 1) & (y == 1))
            fp = np.sum((preds == 1) & (y == 0))
            fn = np.sum((preds == 0) & (y == 1))

            cost = (
                (tp * cost_maintenance) + (fp * cost_inspection) + (fn * cost_downtime)
            )

            if cost < min_cost:
                min_cost = cost
                best_threshold = t

        self.optimal_threshold = best_threshold
        return best_threshold


class FailureTypeClassifier:
    """
    Multi-class classifier wrapper designed to classify the specific failure type
    (e.g., Bearing Failure, Overheating, Pressure Leak, etc.) once a threat is flagged.
    """

    def __init__(self, model_type="xgboost", random_state=42, **kwargs):
        self.model_type = model_type
        self.random_state = random_state
        self.classes_ = None

        if model_type == "logistic_regression":
            self.model = LogisticRegression(
                class_weight="balanced",
                random_state=random_state,
                max_iter=1000,
                **kwargs,
            )
        elif model_type == "random_forest":
            self.model = RandomForestClassifier(
                class_weight="balanced", random_state=random_state, **kwargs
            )
        elif model_type == "xgboost":
            self.model = XGBClassifier(random_state=random_state, **kwargs)
        elif model_type == "lightgbm":
            self.model = LGBMClassifier(
                class_weight="balanced", random_state=random_state, verbose=-1, **kwargs
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")

    def fit(self, X: np.ndarray, y: np.ndarray):
        # y can be a string or integer label encoding the failure mode classes
        self.model.fit(X, y)
        self.classes_ = self.model.classes_
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)
