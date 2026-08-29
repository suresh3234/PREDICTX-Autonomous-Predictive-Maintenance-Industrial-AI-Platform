import logging
from datetime import datetime

import numpy as np
import scipy.stats

logger = logging.getLogger("PredictX.DriftDetection")


class DataDriftDetector:
    """
    Computes statistical data drift using:
    - Kolmogorov-Smirnov (KS) two-sample test (non-parametric comparison).
    - Population Stability Index (PSI) (distribution binning shift indicator).
    """

    def __init__(
        self, baseline_data: np.ndarray = None, feature_names: list[str] = None
    ):
        self.baseline_data = baseline_data
        self.feature_names = feature_names
        self.num_features = 0 if baseline_data is None else baseline_data.shape[1]

    def fit_baseline(self, X_baseline: np.ndarray, feature_names: list[str]):
        self.baseline_data = X_baseline
        self.feature_names = feature_names
        self.num_features = X_baseline.shape[1]
        return self

    def calculate_psi(
        self, baseline_col: np.ndarray, actual_col: np.ndarray, num_buckets=10
    ) -> float:
        """
        Computes the Population Stability Index (PSI) for a continuous variable.
        """
        # Define decile bin boundaries based on baseline quantiles
        percentiles = np.linspace(0, 100, num_buckets + 1)
        bins = np.percentile(baseline_col, percentiles)
        bins[0] = -np.inf
        bins[-1] = np.inf
        bins = np.unique(
            bins
        )  # Deduplicate identical bins (for constant value columns)

        # Calculate frequency counts in each bin
        baseline_counts, _ = np.histogram(baseline_col, bins=bins)
        actual_counts, _ = np.histogram(actual_col, bins=bins)

        # Convert to percentages (fractions)
        baseline_pct = baseline_counts / len(baseline_col)
        actual_pct = actual_counts / len(actual_col)

        # Handle zero percentage bins using epsilon smoothing
        eps = 1e-4
        baseline_pct = np.where(baseline_pct == 0, eps, baseline_pct)
        actual_pct = np.where(actual_pct == 0, eps, actual_pct)

        # Normalize back to sum to 1
        baseline_pct /= np.sum(baseline_pct)
        actual_pct /= np.sum(actual_pct)

        # Compute PSI formula
        psi_val = np.sum(
            (actual_pct - baseline_pct) * np.log(actual_pct / baseline_pct)
        )
        return float(psi_val)

    def detect_drift(self, X_actual: np.ndarray) -> dict:
        """
        Compares incoming actual feature arrays against the stored baseline distributions.
        Returns:
            dict containing feature-level metrics, overall drift ratio, mean PSI, and alert level.
        """
        if self.baseline_data is None or self.feature_names is None:
            raise RuntimeError("Baseline data is not fitted. Call fit_baseline first.")

        if X_actual.shape[1] != self.num_features:
            raise ValueError(
                f"Feature count mismatch: expected {self.num_features}, got {X_actual.shape[1]}"
            )

        feature_drifts = {}
        drifted_count = 0
        psi_values = []

        for i, name in enumerate(self.feature_names):
            baseline_col = self.baseline_data[:, i]
            actual_col = X_actual[:, i]

            # 1. Kolmogorov-Smirnov Test
            ks_stat, p_val = scipy.stats.ks_2samp(baseline_col, actual_col)

            # 2. Population Stability Index
            psi_val = self.calculate_psi(baseline_col, actual_col)
            psi_values.append(psi_val)

            # A feature has drifted if p-value is extremely low (rejection of null hypothesis)
            # OR if the PSI shift is significant (PSI >= 0.25)
            drifted = bool(p_val < 0.05 or psi_val >= 0.25)
            if drifted:
                drifted_count += 1

            feature_drifts[name] = {
                "ks_statistic": float(ks_stat),
                "ks_p_value": float(p_val),
                "psi": psi_val,
                "drifted": drifted,
            }

        drifted_ratio = drifted_count / self.num_features
        mean_psi = float(np.mean(psi_values))

        # Determine overall alert severity
        # OK: stable operational levels
        # WARNING: moderate drift seen on features (ratio >= 0.20 or mean PSI >= 0.10)
        # CRITICAL: significant drift (ratio >= 0.40 or mean PSI >= 0.25) -> Retrain needed
        if drifted_ratio >= 0.40 or mean_psi >= 0.25:
            alert_level = "CRITICAL"
        elif drifted_ratio >= 0.20 or mean_psi >= 0.10:
            alert_level = "WARNING"
        else:
            alert_level = "OK"

        return {
            "feature_level_drift": feature_drifts,
            "drifted_features_ratio": drifted_ratio,
            "mean_psi": mean_psi,
            "alert_level": alert_level,
        }


class AlertSystem:
    """
    Alert dispatch agent. Sends notifications to webhooks or operations logs
    when data drift or degradation thresholds are violated.
    """

    @staticmethod
    def send_alert(
        subject: str, message: str, alert_level: str, webhook_url: str = None
    ) -> dict:
        log_msg = f"[{alert_level} ALERT] {subject}: {message}"
        if alert_level == "CRITICAL":
            logger.critical(log_msg)
        elif alert_level == "WARNING":
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

        alert_payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "subject": subject,
            "message": message,
            "severity": alert_level,
            "webhook_triggered": webhook_url is not None,
        }

        # Simulate webhook request post
        if webhook_url:
            print(f"Triggering Webhook Alert payload to {webhook_url}...")

        return {"status": "DISPATCHED", "payload": alert_payload}
