"""
Prometheus metrics for the dashboard: tickets by channel and outcome, latency, guardrail blocks,
confidence distribution. Safe to import anywhere; recording never raises.
"""
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

TICKETS = Counter("tickets_processed_total", "Tickets processed", ["channel", "decision"])
LATENCY = Histogram("ticket_latency_seconds", "End-to-end latency per ticket",
                    buckets=(0.1, 0.25, 0.5, 1, 2, 3, 5, 10, 30))
GUARDRAIL_BLOCKS = Counter("guardrail_blocks_total", "Responses blocked, by guardrail", ["guardrail"])
CONFIDENCE = Histogram("classification_confidence", "Confidence of the intent classification",
                       buckets=(0.1, 0.3, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0))
ROUTE_REASONS = Counter("routing_reason_total", "Why tickets were routed as they were", ["reason"])


def record(result: dict) -> None:
    try:
        TICKETS.labels(result.get("channel") or "unknown", result.get("decision") or "unknown").inc()
        if result.get("latency_ms") is not None:
            LATENCY.observe(result["latency_ms"] / 1000.0)
        if result.get("confidence") is not None:
            CONFIDENCE.observe(result["confidence"])
        ROUTE_REASONS.labels(result.get("reason_code") or "none").inc()
        for name in ((result.get("guardrails") or {}).get("blocked_by") or []):
            GUARDRAIL_BLOCKS.labels(name).inc()
    except Exception:
        pass


def export() -> tuple:
    return generate_latest(), CONTENT_TYPE_LATEST
