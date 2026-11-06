"""
FastAPI application — HTTP interface for the CloudServe support system.
Provides endpoints for processing tickets and checking system health.
"""
import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="CloudServe Intelligent Support System",
    description=(
        "FDE Capstone — AI-powered customer support routing and response system. "
        "Processes tickets from 4 channels through: ingest → classify → retrieve → "
        "route → generate → validate."
    ),
    version="0.1.0",
)


class TicketRequest(BaseModel):
    ticket_id: str
    channel: str
    subject: Optional[str] = ""
    body: str
    customer_id: Optional[str] = None
    customer_tier: Optional[str] = "standard"
    customer_region: Optional[str] = None
    language_fluency: Optional[str] = "fluent"


class TicketResponse(BaseModel):
    ticket_id: str
    decision: str           # 'auto_respond' or 'escalate'
    response: Optional[str] = None
    citations: Optional[list] = None
    escalation_context: Optional[dict] = None
    confidence: float
    decision_id: str


@app.get("/health")
def health_check():
    """
    Health check endpoint.
    Returns 200 with status 'healthy' when the service is running.
    Used by monitoring and CI to verify the service has started.
    """
    return {"status": "healthy", "version": "0.1.0"}


@app.post("/process", response_model=TicketResponse)
def process_ticket(request: TicketRequest):
    """
    Process a support ticket through the full pipeline:
    ingest → classify → retrieve → route → generate → validate

    Returns the routing decision with either:
    - A drafted response and citations (auto_respond)
    - An escalation context packet (escalate)

    Every call writes to the decision log regardless of outcome.

    Raises:
        HTTPException 422: If ticket data is malformed
        HTTPException 500: If pipeline fails unexpectedly
        HTTPException 501: Until implemented in Week 2 Day 4
    """
    # TODO: implement full pipeline - Week 2 Day 4
    # Pipeline:
    #   1. normalized = ingest.normalize_ticket(request.dict(), request.channel)
    #   2. classification = classify.classify_ticket(normalized)
    #   3. passages = retrieve.retrieve_passages(normalized['body'])
    #   4. routing = route.route_ticket(normalized, classification, passages)
    #   5. if routing['decision'] == 'auto_respond':
    #          response = generate.generate_response(normalized, passages, classification)
    #          guardrail_result = guardrails.run_guardrails(response, normalized, passages, routing)
    #          if guardrail_result['overall_status'] != 'pass': escalate
    #   6. logging_store.log_decision({...})
    raise HTTPException(
        status_code=501,
        detail="Full pipeline not yet implemented — complete in Week 2 Day 4",
    )


@app.get("/decisions/{ticket_id}")
def get_ticket_decisions(ticket_id: str):
    """
    Retrieve all decision log entries for a given ticket_id.
    Useful for auditing and debugging individual tickets.

    Raises:
        HTTPException 501: Until implemented in Week 2 Day 3
    """
    raise HTTPException(
        status_code=501,
        detail="Decision log retrieval not yet implemented — complete in Week 2 Day 3",
    )
