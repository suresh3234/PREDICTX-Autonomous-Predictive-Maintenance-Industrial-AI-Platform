import time
from typing import Any

import numpy as np


class TokenUsageTracker:
    """
    LLMOps Token Consumption, Cost Accounting & Latency Benchmark Tracker.
    """

    # Approximate pricing per 1,000,000 tokens
    MODEL_PRICING = {
        "gemini-1.5-flash": {"input_cost_per_m": 0.075, "output_cost_per_m": 0.30},
        "gemini-1.5-pro": {"input_cost_per_m": 3.50, "output_cost_per_m": 10.50},
        "gpt-4o-mini": {"input_cost_per_m": 0.15, "output_cost_per_m": 0.60},
        "mock-llm": {"input_cost_per_m": 0.00, "output_cost_per_m": 0.00},
    }

    def __init__(self):
        self.invocations: list[dict[str, Any]] = []

    def record_invocation(
        self,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        status: str = "SUCCESS",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Records an LLM execution event and calculates inference cost.
        """
        pricing = self.MODEL_PRICING.get(model_name, {"input_cost_per_m": 0.10, "output_cost_per_m": 0.40})
        input_cost = (prompt_tokens / 1_000_000) * pricing["input_cost_per_m"]
        output_cost = (completion_tokens / 1_000_000) * pricing["output_cost_per_m"]
        total_cost = input_cost + output_cost

        record = {
            "timestamp": time.time(),
            "model_name": model_name,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "latency_ms": round(latency_ms, 2),
            "estimated_cost_usd": round(total_cost, 6),
            "status": status,
            "metadata": metadata or {},
        }
        self.invocations.append(record)
        return record

    def get_summary(self) -> dict[str, Any]:
        """
        Computes aggregate metrics across all tracked invocations.
        """
        if not self.invocations:
            return {
                "total_invocations": 0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "latency_p50_ms": 0.0,
                "latency_p90_ms": 0.0,
                "latency_p99_ms": 0.0,
                "success_rate": 1.0,
            }

        latencies = [r["latency_ms"] for r in self.invocations]
        total_tokens = sum(r["total_tokens"] for r in self.invocations)
        total_cost = sum(r["estimated_cost_usd"] for r in self.invocations)
        successes = sum(1 for r in self.invocations if r["status"] == "SUCCESS")

        return {
            "total_invocations": len(self.invocations),
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 6),
            "latency_p50_ms": round(float(np.percentile(latencies, 50)), 2),
            "latency_p90_ms": round(float(np.percentile(latencies, 90)), 2),
            "latency_p99_ms": round(float(np.percentile(latencies, 99)), 2),
            "success_rate": round(successes / len(self.invocations), 4),
        }
