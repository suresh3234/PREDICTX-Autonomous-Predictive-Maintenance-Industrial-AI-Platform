import contextvars
import time
import uuid
from typing import Any


class Span:
    """
    OpenTelemetry-compatible distributed trace span representation.
    """

    def __init__(
        self,
        name: str,
        trace_id: str,
        span_id: str,
        parent_span_id: str | None = None,
        attributes: dict[str, Any] | None = None,
    ):
        self.name = name
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_span_id = parent_span_id
        self.attributes = attributes or {}
        self.events: list[dict[str, Any]] = []
        self.start_time = time.time()
        self.end_time: float | None = None
        self.status = "UNSET"

    def set_attribute(self, key: str, value: Any):
        self.attributes[key] = value

    def add_event(self, name: str, attributes: dict[str, Any] | None = None):
        self.events.append({
            "name": name,
            "timestamp": time.time(),
            "attributes": attributes or {},
        })

    def end(self, status: str = "OK"):
        self.end_time = time.time()
        self.status = status

    @property
    def duration_ms(self) -> float:
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time) * 1000
        return 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "duration_ms": round(self.duration_ms, 2),
            "status": self.status,
            "attributes": self.attributes,
            "events": self.events,
        }


# Context variable for nested trace hierarchy
_current_span_context = contextvars.ContextVar("current_span", default=None)


class PredictXTracer:
    """
    Distributed OpenTelemetry Tracer for multi-agent workflows and API pipelines.
    """

    def __init__(self, service_name: str = "predictx-backend"):
        self.service_name = service_name
        self.completed_spans: list[Span] = []

    def start_span(self, name: str, attributes: dict[str, Any] | None = None) -> "SpanContextManager":
        return SpanContextManager(self, name, attributes)


class SpanContextManager:
    def __init__(self, tracer: PredictXTracer, name: str, attributes: dict[str, Any] | None = None):
        self.tracer = tracer
        self.name = name
        self.attributes = attributes or {}
        self.span: Span | None = None
        self.token = None

    def __enter__(self) -> Span:
        parent_span = _current_span_context.get()
        if parent_span:
            trace_id = parent_span.trace_id
            parent_id = parent_span.span_id
        else:
            trace_id = uuid.uuid4().hex
            parent_id = None

        span_id = uuid.uuid4().hex[:16]
        self.span = Span(
            name=self.name,
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_id,
            attributes=self.attributes,
        )
        self.token = _current_span_context.set(self.span)
        return self.span

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.span.end(status="ERROR")
            self.span.add_event("exception", {"type": str(exc_type), "message": str(exc_val)})
        else:
            self.span.end(status="OK")

        self.tracer.completed_spans.append(self.span)
        if self.token:
            _current_span_context.reset(self.token)


# Global tracer singleton
tracer = PredictXTracer()
