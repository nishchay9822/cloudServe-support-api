"""
Routing module — decides auto_respond vs escalate using a confidence threshold.
Satisfies acceptance criteria: A5 (routing applies threshold; same input = same output)

CRITICAL: This must be DETERMINISTIC. The same input ticket must always produce
the same routing decision. Do not use random elements.

The threshold is read from .env (CONFIDENCE_THRESHOLD, default 0.80).
Justify your chosen threshold value using evaluation data in the report.

Escalations MUST carry: summary + retrieved sources + reason for uncertainty.
An escalation with context is a feature, not a failure.
"""
import os
from typing import Literal, Optional

CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.80"))

RoutingDecision = Literal["auto_respond", "escalate"]


def route_ticket(
    ticket: dict,
    classification: dict,
    passages: list[dict],
    threshold: Optional[float] = None,
) -> dict:
    """
    Decide whether to auto-respond or escalate a ticket.

    Args:
        ticket: Normalised ticket dict (output of ingest.normalize_ticket)
        classification: Output of classify.classify_ticket()
        passages: Output of retrieve.retrieve_passages()
        threshold: Override the default confidence threshold (for testing only)

    Returns:
        Routing dict with keys:
        - decision (str): 'auto_respond' or 'escalate'
        - reason (str): Human-readable explanation of the routing decision
        - threshold_applied (float): The actual threshold value used
        - escalation_context (dict | None): Present only when decision == 'escalate':
            - summary (str): Brief summary of the ticket
            - retrieved_sources (list): The passages retrieved
            - uncertainty_reason (str): Why confidence was below threshold

    Note:
        Always check ticket.get('labels', {}).get('must_not_auto_respond', False).
        If True, escalate regardless of confidence — this is a safety flag.

    Raises:
        NotImplementedError: Until implemented in Week 2 Day 3
    """
    raise NotImplementedError("TODO: implement route_ticket() - Week 2 Day 3")
