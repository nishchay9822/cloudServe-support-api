"""The dashboard and alert rules may only query metrics the API really exposes."""
import json
import os
import re
import pytest
from fastapi.testclient import TestClient
from tests.conftest import ROOT, find_ticket
from src.api import app
MON = os.path.join(ROOT, "monitoring")
METRIC = re.compile(r"\b(tickets_processed_total|ticket_latency_seconds(?:_bucket)?|guardrail_blocks_total|"
                    r"classification_confidence(?:_bucket)?|routing_reason_total)\b")
def _exprs():
    d = json.load(open(os.path.join(MON, "grafana", "dashboards", "cloudserve.json")))
    out = [t["expr"] for p in d["panels"] for t in p["targets"]]
    out += re.findall(r"expr:\s*(.+)", open(os.path.join(MON, "alerts.yml")).read())
    return d, out
def payload(t):
    return {k: t[k] for k in ("ticket_id", "channel", "subject", "body", "customer_id", "customer_name", "customer_tier", "customer_region", "language_fluency")}
def test_dashboard_has_the_five_required_views():
    d, _ = _exprs()
    titles = " ".join(p["title"] for p in d["panels"])
    for n in ("1.", "2.", "3.", "4.", "5."):
        assert n in titles
    assert len(d["panels"]) >= 5
def test_every_queried_metric_is_exposed_by_the_api(fake_llm):
    with TestClient(app) as c:
        c.post("/process", json=payload(find_ticket("rollback_request")))                       # auto reply
        c.post("/process", json=payload(find_ticket("security_incident", "escalate")))          # escalation
        text = c.get("/metrics").text
    _, exprs = _exprs()
    used = {m for e in exprs for m in METRIC.findall(e)}
    assert used, "no metrics found in dashboard or alerts"
    missing = [m for m in used if m not in text]
    assert not missing, f"dashboard/alerts query metrics the API does not expose: {missing}"
def test_prometheus_scrapes_the_api_metrics_path():
    cfg = open(os.path.join(MON, "prometheus.yml")).read()
    assert "/metrics" in cfg and ":8000" in cfg
