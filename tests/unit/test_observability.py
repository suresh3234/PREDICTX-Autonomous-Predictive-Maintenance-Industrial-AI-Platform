from fastapi.testclient import TestClient

from apps.api.app.main import app
from src.observability.aiops_correlator import AIOpsIncidentCorrelator
from src.observability.metrics import PrometheusMetricsCollector
from src.observability.tracing import PredictXTracer


def test_prometheus_metrics_collection_and_format():
    collector = PrometheusMetricsCollector()

    collector.record_inference(model_type="xgboost_classifier", status="success", latency_sec=0.045)
    collector.record_anomaly(machine_id="M1000", severity="CRITICAL")
    collector.record_drift(feature_name="vibration", drift_score=0.082)
    collector.record_agent_invocation(agent_name="InvestigatorAgent")
    collector.record_hitl_request(status="PENDING")

    text = collector.generate_prometheus_text()

    assert "predictx_inference_requests_total" in text
    assert 'model_type="xgboost_classifier"' in text
    assert 'severity="CRITICAL"' in text
    assert 'predictx_model_drift_score{feature="vibration"} 0.0820' in text
    assert 'predictx_agent_invocations_total{agent="InvestigatorAgent"} 1' in text
    assert 'predictx_hitl_approval_requests_total{status="PENDING"} 1' in text


def test_opentelemetry_distributed_tracing():
    tracer = PredictXTracer(service_name="test-service")

    with tracer.start_span("root_investigation", attributes={"machine_id": "M1000"}) as root_span:
        root_span.set_attribute("env", "production")
        root_span.add_event("sensor_loaded", {"vibration": 4.2})

        with tracer.start_span("nested_rca_diagnostic") as child_span:
            child_span.set_attribute("failure_mode", "Bearing Wear")

    assert len(tracer.completed_spans) == 2

    child = tracer.completed_spans[0]
    root = tracer.completed_spans[1]

    assert child.name == "nested_rca_diagnostic"
    assert root.name == "root_investigation"
    assert child.trace_id == root.trace_id
    assert child.parent_span_id == root.span_id
    assert root.status == "OK"
    assert child.duration_ms >= 0


def test_aiops_incident_correlation_and_cascade_detection():
    correlator = AIOpsIncidentCorrelator(time_window_seconds=60.0)

    # Ingest isolated alert on M1000
    res1 = correlator.ingest_alert(
        machine_id="M1000",
        severity="CRITICAL",
        sensor="vibration",
        message="Vibration exceeded threshold",
        zone="Zone-A",
    )
    assert res1["correlation_cluster"]["cluster_type"] == "ISOLATED_INCIDENT"

    # Ingest second alert on M1001 in same Zone-A (Cascade!)
    res2 = correlator.ingest_alert(
        machine_id="M1001",
        severity="CRITICAL",
        sensor="temperature",
        message="Overheating detected",
        zone="Zone-A",
    )
    assert res2["correlation_cluster"]["cluster_type"] == "PLANT_ZONE_CASCADE_EVENT"
    assert len(res2["correlation_cluster"]["involved_machines"]) == 2
    assert "Zone-A" in res2["correlation_cluster"]["recommendation"]


def test_fastapi_metrics_endpoint():
    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "predictx_inference_requests_total" in response.text
