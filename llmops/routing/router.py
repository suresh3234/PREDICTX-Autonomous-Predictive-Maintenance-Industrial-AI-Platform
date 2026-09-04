import logging
import time
from collections.abc import Callable
from typing import Any

from llmops.cache.semantic_cache import SemanticCache
from llmops.tracking.tracker import TokenUsageTracker

logger = logging.getLogger("PredictX.LLMOps.Router")


class ResilientLLMRouter:
    """
    Resilient LLM Inference Router with Semantic Caching, Circuit Breaker, and Fallback Routing.
    """

    def __init__(
        self,
        cache: SemanticCache | None = None,
        tracker: TokenUsageTracker | None = None,
        failure_threshold: int = 3,
        cooldown_seconds: float = 30.0,
    ):
        self.cache = cache or SemanticCache()
        self.tracker = tracker or TokenUsageTracker()
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds

        self._consecutive_failures = 0
        self._circuit_state = "CLOSED"  # "CLOSED" (Normal), "OPEN" (Tripped)
        self._last_state_change = time.time()

    def _check_circuit(self) -> str:
        """Evaluates circuit breaker health state."""
        if self._circuit_state == "OPEN":
            if (time.time() - self._last_state_change) > self.cooldown_seconds:
                self._circuit_state = "HALF_OPEN"
                logger.info("Circuit Breaker transitioned to HALF_OPEN")
        return self._circuit_state

    def _record_success(self):
        self._consecutive_failures = 0
        self._circuit_state = "CLOSED"

    def _record_failure(self):
        self._consecutive_failures += 1
        if self._consecutive_failures >= self.failure_threshold:
            self._circuit_state = "OPEN"
            self._last_state_change = time.time()
            logger.warning("Circuit Breaker TRIPPED to OPEN state due to repeated failures.")

    def generate(
        self,
        query: str,
        primary_callable: Callable[[], str],
        fallback_callable: Callable[[], str] | None = None,
        model_name: str = "gemini-1.5-flash",
    ) -> dict[str, Any]:
        """
        Executes query through Semantic Cache -> Primary LLM -> Fallback LLM.
        """
        start_time = time.time()

        # Step 1: Check Semantic Cache
        cached = self.cache.get(query)
        if cached:
            latency = (time.time() - start_time) * 1000
            self.tracker.record_invocation(
                model_name=f"{model_name}-cached",
                prompt_tokens=len(query.split()),
                completion_tokens=len(cached["response"].split()),
                latency_ms=latency,
                status="SUCCESS",
            )
            return {
                "response": cached["response"],
                "source": "SEMANTIC_CACHE",
                "similarity": cached["similarity"],
                "latency_ms": round(latency, 2),
            }

        # Step 2: Check Circuit Breaker
        state = self._check_circuit()
        response_text = None
        source = "PRIMARY_MODEL"

        if state != "OPEN":
            try:
                response_text = primary_callable()
                self._record_success()
            except Exception as e:
                logger.error(f"Primary model failed: {e}")
                self._record_failure()

        # Step 3: Fallback Execution
        if response_text is None:
            source = "FALLBACK_MODEL"
            if fallback_callable:
                try:
                    response_text = fallback_callable()
                except Exception as fb_err:
                    logger.error(f"Fallback model failed: {fb_err}")
                    response_text = "System alert: AI diagnostic service temporarily unavailable."
            else:
                response_text = "Operational notice: Fallback diagnostic rules triggered."

        # Step 4: Record Token & Latency Telemetry
        latency = (time.time() - start_time) * 1000
        p_tokens = len(query.split()) * 2
        c_tokens = len(response_text.split()) * 2

        self.tracker.record_invocation(
            model_name=model_name if source == "PRIMARY_MODEL" else "fallback",
            prompt_tokens=p_tokens,
            completion_tokens=c_tokens,
            latency_ms=latency,
            status="SUCCESS" if response_text else "FAILED",
        )

        # Step 5: Update Semantic Cache
        if source == "PRIMARY_MODEL" and response_text:
            self.cache.set(query, response_text)

        return {
            "response": response_text,
            "source": source,
            "latency_ms": round(latency, 2),
            "circuit_state": self._circuit_state,
        }
