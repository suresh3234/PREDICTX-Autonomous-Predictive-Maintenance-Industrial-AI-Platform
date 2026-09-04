from llmops.cache.semantic_cache import SemanticCache
from llmops.prompts.registry import PromptRegistry
from llmops.routing.router import ResilientLLMRouter
from llmops.tracking.tracker import TokenUsageTracker


def test_prompt_registry_loading_and_render():
    registry = PromptRegistry()

    # Render supervisor prompt
    rendered = registry.render(
        agent_name="supervisor",
        variables={
            "machine_id": "M1000",
            "vibration": "4.2",
            "temperature": "78.0",
            "pressure": "100.0",
            "current": "12.0",
        },
    )

    assert rendered["version"] == "1.0.0"
    assert rendered["agent"] == "supervisor"
    assert "M1000" in rendered["user_prompt"]
    assert "4.2 mm/s" in rendered["user_prompt"]
    assert "Chief Reliability Supervisor" in rendered["system_prompt"]


def test_semantic_cache_hit_and_miss():
    cache = SemanticCache(similarity_threshold=0.90)

    # Initial query miss
    q1 = "How to replace defective ball bearings on high vibration?"
    ans1 = "Shut down the machine immediately and replace defective ball bearings with lithium grease."
    assert cache.get(q1) is None

    # Cache response
    cache.set(q1, ans1)

    # Exact or semantically equivalent query hit
    q1_variant = "What is the procedure to replace defective ball bearings when high vibration occurs?"
    hit = cache.get(q1_variant)
    assert hit is not None
    assert hit["response"] == ans1
    assert hit["similarity"] >= 0.85

    # Completely different query miss
    q2 = "What are the cafeteria operating hours?"
    assert cache.get(q2) is None

    stats = cache.get_stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 2


def test_token_usage_and_cost_tracker():
    tracker = TokenUsageTracker()

    tracker.record_invocation(
        model_name="gemini-1.5-flash",
        prompt_tokens=1000,
        completion_tokens=500,
        latency_ms=120.5,
    )
    tracker.record_invocation(
        model_name="gpt-4o-mini",
        prompt_tokens=2000,
        completion_tokens=1000,
        latency_ms=250.0,
    )

    summary = tracker.get_summary()
    assert summary["total_invocations"] == 2
    assert summary["total_tokens"] == 4500
    assert summary["total_cost_usd"] > 0
    assert summary["latency_p50_ms"] > 100.0
    assert summary["success_rate"] == 1.0


def test_resilient_llm_router_caching_and_fallback():
    router = ResilientLLMRouter(failure_threshold=2)

    # 1. Primary Success
    res1 = router.generate(
        query="Explain hydraulic pressure drops",
        primary_callable=lambda: "Hydraulic pressure drops indicate manifold O-ring seal rupture.",
    )
    assert res1["source"] == "PRIMARY_MODEL"
    assert "O-ring" in res1["response"]

    # 2. Second Query Served from Semantic Cache
    res2 = router.generate(
        query="Explain hydraulic pressure drops",
        primary_callable=lambda: "This should not be called because of cache hit.",
    )
    assert res2["source"] == "SEMANTIC_CACHE"
    assert "O-ring" in res2["response"]

    # 3. Fallback Triggered on Primary Exception
    def faulty_primary():
        raise ConnectionError("Upstream LLM timeout")

    res3 = router.generate(
        query="Diagnose thermal radiator issue",
        primary_callable=faulty_primary,
        fallback_callable=lambda: "Fallback: Clean dust from radiator intake filters.",
    )
    assert res3["source"] == "FALLBACK_MODEL"
    assert "Clean dust" in res3["response"]
