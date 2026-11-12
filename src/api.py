"""
HTTP interface for the CloudServe support system (FastAPI).

    uvicorn src.api:app --port 8000

POST /process  runs the full pipeline on one ticket and logs the decision.
GET  /health   liveness plus readiness of the parts the pipeline needs.
GET  /decisions/{ticket_id}  the logged decisions for a ticket (audit trail).
GET  /metrics  Prometheus metrics.
POST /admin/kill-switch  on/off: when on, every ticket is escalated to a human.
"""
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field

from src import llm, logging_store, pipeline, telemetry

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging_store.init_db()
    pipeline.warm_up()
    yield


app = FastAPI(title="CloudServe Intelligent Support System", version="1.0.0", lifespan=lifespan,
              description="Ingest, classify, retrieve, route, generate, validate. Every decision is logged.")


class TicketRequest(BaseModel):
    ticket_id: str = Field(..., min_length=1)
    channel: str
    subject: Optional[str] = ""
    body: str = ""
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_tier: Optional[str] = "standard"
    customer_region: Optional[str] = None
    language_fluency: Optional[str] = "fluent"
    received_at: Optional[str] = None


@app.get("/health")
def health():
    return {"status": "healthy", "version": app.version, "model_provider_configured": llm.is_available(),
            "kill_switch": pipeline.kill_switch_on()}


@app.post("/process")
def process(req: TicketRequest):
    """Always returns a decision. Provider trouble becomes an escalation, never a 500."""
    result = pipeline.process_ticket(req.model_dump(), run_id="api")
    if result["status"] == "error" and result["reason_code"] == "pipeline_error" and result.get("error", "").startswith("ValueError"):
        raise HTTPException(status_code=422, detail=result["error"])
    return {
        "ticket_id": result["ticket_id"], "decision": result["decision"], "reason": result["reason"],
        "reason_code": result["reason_code"], "intent": result["intent"], "urgency": result["urgency"],
        "confidence": result["confidence"], "response": result["response_text"], "citations": result["citations"],
        "escalation_context": result["escalation_context"], "decision_id": result.get("decision_id"),
        "latency_ms": result["latency_ms"],
    }


@app.get("/decisions/{ticket_id}")
def decisions(ticket_id: str):
    rows = logging_store.get_decisions_for_ticket(ticket_id)
    if not rows:
        raise HTTPException(status_code=404, detail="no decisions logged for that ticket")
    return rows


@app.get("/metrics")
def metrics():
    body, ctype = telemetry.export()
    return Response(content=body, media_type=ctype)


class KillSwitch(BaseModel):
    on: bool
    token: str = ""


@app.post("/admin/kill-switch")
def kill_switch(req: KillSwitch):
    """Takes effect on the next ticket. In-flight tickets finish normally; later ones go to humans."""
    if not ADMIN_TOKEN or req.token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="admin token required (set ADMIN_TOKEN)")
    path = os.path.join(pipeline.ROOT, "storage", "KILL_SWITCH")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if req.on:
        open(path, "w").write("on")
    elif os.path.exists(path):
        os.remove(path)
    return {"kill_switch": pipeline.kill_switch_on()}
