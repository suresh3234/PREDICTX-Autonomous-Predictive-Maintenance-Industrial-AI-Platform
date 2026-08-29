import time
from collections import defaultdict
from typing import Any, Optional


class PrometheusMetricsCollector:
    """
    In-memory Prometheus Metrics Collector and Exporter for PredictX.
    Exposes industrial ML, agentic AI, and system health metrics in standard Prometheus exposition format.
    """

    def __init__(self):
        # Metric state stores
        self.inference_requests = defaultdict(int)  # key: (model_type, status)
        self.inference_latencies = defaultdict(list)  # key: (model_type)
        self.anomalies_detected = defaultdict(int)  # key: (machine_id, severity)
        self.drift_scores = {}  # key: feature_name -> score
        self.agent_invocations = defaultdict(int)  # key: (agent_name)
        self.hitl_requests = defaultdict(int)  # key: (status)

    def record_inference(self, model_type: str, status: str = "success", latency_sec: float = 0.0):
        """Records an inference execution event."""
        self.inference_requests[(model_type, status)] += 1
        if latency_sec > 0:
            self.inference_latencies[model_type].append(latency_sec)

    def record_anomaly(self, machine_id: str, severity: str):
        """Records an anomalous equipment event."""
        self.anomalies_detected[(machine_id, severity.upper())] += 1

    def record_drift(self, feature_name: str, drift_score: float):
        """Records feature drift metric (e.g. KS-statistic or PSI)."""
        self.drift_scores[feature_name] = float(drift_score)

    def record_agent_invocation(self, agent_name: str):
        """Records execution of an autonomous AI agent."""
        self.agent_invocations[agent_name] += 1

    def record_hitl_request(self, status: str):
        """Records a human-in-the-loop approval gate state."""
        self.hitl_requests[status.upper()] += 1

    def generate_prometheus_text(self) -> str:
        """
        Generates standard Prometheus plaintext metric exposition.
        """
        lines = []

        # 1. Inference Requests Total
        lines.append("# HELP predictx_inference_requests_total Total number of ML inference requests.")
        lines.append("# TYPE predictx_inference_requests_total counter")
        for (mtype, status), count in self.inference_requests.items():
            lines.append(f'predictx_inference_requests_total{{model_type="{mtype}",status="{status}"}} {count}')
        if not self.inference_requests:
            lines.append('predictx_inference_requests_total{model_type="default",status="success"} 0')

        # 2. Inference Latency Seconds
        lines.append("\n# HELP predictx_inference_latency_seconds_sum Total inference execution duration in seconds.")
        lines.append("# TYPE predictx_inference_latency_seconds_sum counter")
        for mtype, lats in self.inference_latencies.items():
            lines.append(f'predictx_inference_latency_seconds_sum{{model_type="{mtype}"}} {sum(lats):.4f}')
            lines.append(f'predictx_inference_latency_seconds_count{{model_type="{mtype}"}} {len(lats)}')

        # 3. Anomalies Detected Total
        lines.append("\n# HELP predictx_anomalies_detected_total Total equipment anomalies detected.")
        lines.append("# TYPE predictx_anomalies_detected_total counter")
        for (mid, sev), count in self.anomalies_detected.items():
            lines.append(f'predictx_anomalies_detected_total{{machine_id="{mid}",severity="{sev}"}} {count}')
        if not self.anomalies_detected:
            lines.append('predictx_anomalies_detected_total{machine_id="M1000",severity="NORMAL"} 0')

        # 4. Feature Drift Scores
        lines.append("\n# HELP predictx_model_drift_score Current Kolmogorov-Smirnov drift statistic per feature.")
        lines.append("# TYPE predictx_model_drift_score gauge")
        for feat, score in self.drift_scores.items():
            lines.append(f'predictx_model_drift_score{{feature="{feat}"}} {score:.4f}')

        # 5. Agent Invocations Total
        lines.append("\n# HELP predictx_agent_invocations_total Total execution count of specialized AI agents.")
        lines.append("# TYPE predictx_agent_invocations_total counter")
        for agent, count in self.agent_invocations.items():
            lines.append(f'predictx_agent_invocations_total{{agent="{agent}"}} {count}')

        # 6. HITL Approval Requests Total
        lines.append("\n# HELP predictx_hitl_approval_requests_total Total human-in-the-loop approval gate requests.")
        lines.append("# TYPE predictx_hitl_approval_requests_total counter")
        for status, count in self.hitl_requests.items():
            lines.append(f'predictx_hitl_approval_requests_total{{status="{status}"}} {count}')

        return "\n".join(lines) + "\n"


# Global singleton instance
metrics_collector = PrometheusMetricsCollector()
