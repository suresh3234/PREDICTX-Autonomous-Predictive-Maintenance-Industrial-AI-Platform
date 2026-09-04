import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from agents.supervisor.supervisor import SupervisorAgent
from apps.api.app.main import app
from hitl.approval_gate import ApprovalGateManager
from hitl.audit_trail import ImmutableAuditTrail
from ml.anomaly.models import IsolationForestDetector
from ml.classification.models import FailureThreatClassifier
from ml.features.pipelines import FeaturePipeline
from ml.rul.models import RandomForestRULRegressor
from rag.generator import RAGGenerator
from rag.vector_store import HybridRetriever
from src.security.auth import create_access_token, decode_access_token


def test_full_platform_end_to_end_pipeline():
    """
    End-to-End full system integration test covering:
    Raw Telemetry Ingestion -> Feature Pipeline -> ML Inference -> RAG ->
    Multi-Agent Collaboration -> HITL Safety Gate -> Cryptographic Audit Trail -> REST API.
    """
    # 1. Telemetry Ingestion & Feature Engineering
    records = []
    base_time = pd.Timestamp("2026-08-29 12:00:00")
    for i in range(25):
        records.append({
            "machine_id": "M1047",
            "timestamp": (base_time + pd.Timedelta(minutes=5 * i)).strftime("%Y-%m-%d %H:%M:%S"),
            "machine_type": "CNC Milling",
            "temperature": 70.0 + i * 0.3,
            "vibration": 3.0 + (i % 2) * 0.5,
            "pressure": 98.2,
            "rpm": 1850.0,
            "voltage": 415.0,
            "current": 14.8,
            "power": 6.2,
            "humidity": 42.0,
            "load": 84.5,
            "operating_hours": 4120.0 + i * 0.1,
            "maintenance_count": 2,
            "last_maintenance": "2026-08-17 00:00:00",
        })
    raw_df = pd.DataFrame(records)

    pipeline = FeaturePipeline(rolling_windows=[3])
    feat_df = pipeline.transform(raw_df, drop_na=False)
    assert "feature_temp_x_vib" in feat_df.columns

    # 2. Multi-Model ML Inference
    classifier = FailureThreatClassifier()
    anomaly_detector = IsolationForestDetector()
    rul_predictor = RandomForestRULRegressor()

    X_synth = np.array([
        [65.0, 1.5, 100.0, 1800.0, 3000.0, 5.0],
        [78.4, 4.25, 98.2, 1850.0, 4120.0, 12.0],
    ])
    y_synth_cls = np.array([0, 1])
    y_synth_rul = np.array([500.0, 143.0])

    classifier.fit(X_synth, y_synth_cls)
    anomaly_detector.fit(X_synth)
    rul_predictor.fit(X_synth, y_synth_rul)

    features = np.array([[78.4, 4.25, 98.2, 1850.0, 4120.0, 12.0]])
    preds = classifier.predict(features)
    assert preds is not None

    anomalies = anomaly_detector.predict_score(features)
    assert anomalies is not None

    rul_est = rul_predictor.predict(features)
    assert rul_est is not None

    # 3. RAG Retrieval & Diagnostic Synthesis
    retriever = HybridRetriever()
    retriever.index_documents([
        {
            "id": "doc_skf_bearing",
            "text": "For severe vibration on CNC milling drives, replace SKF-6205 bearing immediately with LOTO safety isolation.",
            "metadata": {"source": "SKF-Manual"},
        },
        {
            "id": "doc_coolant",
            "text": "Check radiator lines if temperature exceeds 80 degrees Celsius.",
            "metadata": {"source": "Cooling-SOP"},
        },
    ])
    generator = RAGGenerator(retriever=retriever, api_key=None)
    rag_res = generator.generate_response(
        query="vibration high squealing bearing failure",
        telemetry={"temperature": 78.4, "vibration": 4.25},
        predictions={"anomaly_severity": "CRITICAL", "failure_type": "Bearing Failure", "predicted_rul": 143.0},
    )
    assert rag_res is not None
    assert "response" in rag_res

    # 4. Multi-Agent Autonomous Reasoning
    supervisor = SupervisorAgent()
    investigation_result = supervisor.run_investigation(
        telemetry={"machine_id": "M1047", "temperature": 78.4, "vibration": 4.25, "pressure": 98.2},
        predictions={"is_anomalous": True, "failure_probability": 0.87, "predicted_failure_type": "Bearing Wear"},
    )
    assert investigation_result["overall_status"] in ["CRITICAL ACTION REQUIRED", "NOMINAL"]
    assert "M1047" in investigation_result["machine_id"]

    # 5. Human-in-the-Loop Gate & Cryptographic Audit Trail
    gate_mgr = ApprovalGateManager()
    gate = gate_mgr.request_approval(
        action_type="emergency_shutdown",
        machine_id="M1047",
        justification="Excessive vibration harmonics",
        action_payload={"target": "M1047", "action": "EMERGENCY_SHUTDOWN"},
    )
    assert gate["status"] == "PENDING"
    req_id = gate["request_id"]
    approved_res = gate_mgr.approve_request(request_id=req_id, approver_id="engineer_alice")
    assert approved_res["status"] == "APPROVED"

    audit_trail = ImmutableAuditTrail()
    b1 = audit_trail.log_event(
        event_type="HITL_APPROVED", actor_id="engineer_alice", machine_id="M1047", action="EMERGENCY_SHUTDOWN"
    )
    assert b1["hash"] is not None
    assert audit_trail.verify_chain_integrity() is True

    # 6. REST API Gateway & Security Tokens
    token = create_access_token(subject="admin_user", role="ADMIN")
    decoded = decode_access_token(token)
    assert decoded["sub"] == "admin_user"

    client = TestClient(app)
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    res_metrics = client.get("/metrics")
    assert res_metrics.status_code == 200
    assert "predictx_inference_requests_total" in res_metrics.text
