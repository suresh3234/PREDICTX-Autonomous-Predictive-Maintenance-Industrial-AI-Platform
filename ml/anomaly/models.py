import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM


class BaseAnomalyDetector:
    def __init__(self):
        self.thresholds = {}

    def _compute_thresholds(self, train_scores: np.ndarray):
        """Computes score percentiles on training data to map future scores to severity and probability."""
        self.thresholds = {
            "median": float(np.percentile(train_scores, 50)),
            "p90": float(np.percentile(train_scores, 90)),
            "p95": float(np.percentile(train_scores, 95)),
            "p98": float(np.percentile(train_scores, 98)),
            "p99_5": float(np.percentile(train_scores, 99.5)),
            "max": float(np.max(train_scores)),
        }

    def predict_details(
        self, X: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, list[str]]:
        """
        Computes details for input X.
        Returns:
            - scores: Raw anomaly scores
            - probabilities: Normalized anomaly probability (0.0 to 1.0)
            - severities: List of severity strings
        """
        scores = self.predict_score(X)
        probabilities = []
        severities = []

        p50 = self.thresholds.get("median", 0.0)
        p90 = self.thresholds.get("p90", 1.0)
        p95 = self.thresholds.get("p95", 1.5)
        p98 = self.thresholds.get("p98", 2.0)
        p99_5 = self.thresholds.get("p99_5", 3.0)

        for score in scores:
            # 1. Map score to severity
            if score < p90:
                severity = "NORMAL"
            elif score < p95:
                severity = "LOW"
            elif score < p98:
                severity = "MEDIUM"
            elif score < p99_5:
                severity = "HIGH"
            else:
                severity = "CRITICAL"
            severities.append(severity)

            # 2. Map score to probability using linear interpolation between thresholds
            if score <= p50:
                prob = 0.0 + (score / (p50 + 1e-8)) * 0.1
            elif score <= p95:
                prob = 0.1 + ((score - p50) / (p95 - p50 + 1e-8)) * 0.4
            elif score <= p99_5:
                prob = 0.5 + ((score - p95) / (p99_5 - p95 + 1e-8)) * 0.4
            else:
                # Cap probability at 1.0
                prob = 0.9 + min(
                    ((score - p99_5) / (max(score, p99_5 * 2) - p99_5 + 1e-8)) * 0.1,
                    0.1,
                )

            probabilities.append(float(np.clip(prob, 0.0, 1.0)))

        return scores, np.array(probabilities), severities


class StatisticalThresholdDetector(BaseAnomalyDetector):
    """Statistical detector computing Z-score thresholds on key features."""

    def __init__(self):
        super().__init__()
        self.means = None
        self.stds = None

    def fit(self, X: np.ndarray):
        self.means = np.mean(X, axis=0)
        self.stds = np.std(X, axis=0) + 1e-8  # avoid div by zero
        train_scores = self.predict_score(X)
        self._compute_thresholds(train_scores)
        return self

    def predict_score(self, X: np.ndarray) -> np.ndarray:
        # Z-score: score is the max absolute Z-score across features
        z_scores = np.abs((X - self.means) / self.stds)
        return np.max(z_scores, axis=1)


class IsolationForestDetector(BaseAnomalyDetector):
    """Isolation Forest anomaly detector wrapper."""

    def __init__(self, n_estimators=100, contamination=0.05, random_state=42):
        super().__init__()
        self.model = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1,
        )

    def fit(self, X: np.ndarray):
        self.model.fit(X)
        train_scores = self.predict_score(X)
        self._compute_thresholds(train_scores)
        return self

    def predict_score(self, X: np.ndarray) -> np.ndarray:
        # decision_function returns negative values for outliers, positive for inliers.
        # We invert it: higher score = more anomalous.
        return -self.model.decision_function(X)


class OneClassSVMDetector(BaseAnomalyDetector):
    """One-Class SVM anomaly detector wrapper."""

    def __init__(self, nu=0.05, kernel="rbf", gamma="scale"):
        super().__init__()
        self.model = OneClassSVM(nu=nu, kernel=kernel, gamma=gamma)

    def fit(self, X: np.ndarray):
        self.model.fit(X)
        train_scores = self.predict_score(X)
        self._compute_thresholds(train_scores)
        return self

    def predict_score(self, X: np.ndarray) -> np.ndarray:
        # Invert decision function: higher score = more anomalous
        return -self.model.decision_function(X)


class AutoencoderPyTorch(nn.Module):
    def __init__(self, input_dim, encoding_dim=8):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, encoding_dim * 2),
            nn.ReLU(),
            nn.Linear(encoding_dim * 2, encoding_dim),
            nn.ReLU(),
        )
        self.decoder = nn.Sequential(
            nn.Linear(encoding_dim, encoding_dim * 2),
            nn.ReLU(),
            nn.Linear(encoding_dim * 2, input_dim),
        )

    def forward(self, x):
        return self.decoder(self.encoder(x))


class AutoencoderDetector(BaseAnomalyDetector):
    """Unsupervised Autoencoder neural network anomaly detector."""

    def __init__(self, encoding_dim=8, epochs=15, batch_size=64, lr=0.005):
        super().__init__()
        self.encoding_dim = encoding_dim
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
        self.model = None

    def fit(self, X: np.ndarray):
        input_dim = X.shape[1]
        self.model = AutoencoderPyTorch(input_dim, self.encoding_dim)

        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=self.lr)

        # Convert X to PyTorch tensor
        dataset = torch.tensor(X, dtype=torch.float32)
        dataloader = torch.utils.data.DataLoader(
            dataset, batch_size=self.batch_size, shuffle=True
        )

        self.model.train()
        for _epoch in range(self.epochs):
            for batch in dataloader:
                optimizer.zero_grad()
                outputs = self.model(batch)
                loss = criterion(outputs, batch)
                loss.backward()
                optimizer.step()

        train_scores = self.predict_score(X)
        self._compute_thresholds(train_scores)
        return self

    def predict_score(self, X: np.ndarray) -> np.ndarray:
        self.model.eval()
        dataset = torch.tensor(X, dtype=torch.float32)
        with torch.no_grad():
            reconstructions = self.model(dataset)
            # Reconstructions errors (MSE per sample)
            errors = torch.mean((dataset - reconstructions) ** 2, dim=1)
        return errors.numpy()
