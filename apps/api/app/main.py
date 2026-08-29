from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from app.api.v1.router import router
from app.core.config import settings
from app.db import Base
from app.db.session import engine
from src.observability.metrics import metrics_collector


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="PredictX Autonomous Predictive Maintenance & Industrial AI Platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["system"])
def root():
    return {
        "platform": "PredictX Autonomous Predictive Maintenance Platform",
        "status": "ONLINE",
        "version": "1.0.0",
        "documentation": "/docs",
        "health_check": "/health",
        "prometheus_metrics": "/metrics",
        "endpoints": {
            "direct_inference": "/api/v1/predict/direct",
            "fleet_predictions": "/api/v1/fleet/predictions",
            "model_registry": "/api/v1/models",
            "drift_monitoring": "/api/v1/monitoring/drift",
            "retraining_pipeline": "/api/v1/retrain",
            "rag_knowledge_base": "/api/v1/rag/documents",
            "rag_search": "/api/v1/rag/search",
            "ai_copilot": "/api/v1/copilot/query",
            "multi_agent_fleet": "/api/v1/agents/fleet",
            "agent_investigate": "/api/v1/agents/investigate",
            "mcp_servers": "/api/v1/mcp/servers",
            "mcp_execute": "/api/v1/mcp/execute",
            "hitl_requests": "/api/v1/hitl/requests",
            "hitl_approve": "/api/v1/hitl/approve",
            "hitl_audit_trail": "/api/v1/hitl/audit",
            "incidents": "/api/v1/incidents",
            "work_orders": "/api/v1/work-orders",
            "observability_stats": "/api/v1/observability/stats"
        }
    }


@app.get("/health", tags=["system"])
def health():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.environment,
    }


@app.get("/ready", tags=["system"])
def readiness():
    return {
        "status": "ready",
    }


@app.get("/metrics", response_class=PlainTextResponse, tags=["observability"])
def prometheus_metrics():
    return metrics_collector.generate_prometheus_text()


app.include_router(
    router,
    prefix=settings.api_v1_prefix,
)
