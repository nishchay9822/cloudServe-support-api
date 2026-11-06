"""
Guardrails module — 5 guardrails that run on every response and can block it.
Satisfies acceptance criteria: A7 (at least one guardrail can block and does so when triggered)

ALL 5 guardrails MUST run on EVERY response, including during the evaluation run.
Guardrails disabled by a flag during the actual run = A7 failure.

Guardrail 1 (PII):           Names, addresses, keys, account numbers in outbound → Block + escalate
Guardrail 2 (Grounding):     Every factual claim must trace to a retrieved passage → Block + escalate
Guardrail 3 (Injection):     Ticket text hasn't altered system instructions       → Block + escalate + record
Guardrail 4 (Tone/Scope):    No refund promises or timeline commitments           → Block
Guardrail 5 (Conf. Floor):   Routing threshold was actually applied               → Escalate
"""
import re
from typing import Literal, Optional

GuardrailStatus = Literal["pass", "block", "escalate"]


def check_pii(response_text: str) -> dict:
    """
    Guardrail 1: Check for PII in outbound response.
    Detects: email addresses, phone numbers, account numbers, API keys,
             credit card patterns, SSN patterns.

    Returns:
        {
            "status": "pass" | "block",
            "reason": str,
            "detected_patterns": list[str]
        }

    Raises:
        NotImplementedError: Until implemented in Week 2 Day 4
    """
    raise NotImplementedError("TODO: Guardrail 1 (PII) - implement Week 2 Day 4")


def check_grounding(response_text: str, passages: list[dict]) -> dict:
    """
    Guardrail 2: Verify every factual claim traces to a retrieved passage.
    If the response makes claims not supported by any passage, block it.

    Returns:
        {
            "status": "pass" | "block",
            "reason": str,
            "ungrounded_claims": list[str]
        }

    Raises:
        NotImplementedError: Until implemented in Week 2 Day 4
    """
    raise NotImplementedError("TODO: Guardrail 2 (Grounding) - implement Week 2 Day 4")


def check_injection(ticket_body: str, system_prompt: str) -> dict:
    """
    Guardrail 3: Detect prompt injection — ticket text attempting to alter system instructions.
    Look for patterns like 'ignore previous instructions', role-playing requests,
    instruction overrides in ticket body.

    Returns:
        {
            "status": "pass" | "block",
            "reason": str,
            "suspicious_patterns": list[str]
        }

    Raises:
        NotImplementedError: Until implemented in Week 2 Day 4
    """
    raise NotImplementedError("TODO: Guardrail 3 (Injection) - implement Week 2 Day 4")


def check_tone_scope(response_text: str) -> dict:
    """
    Guardrail 4: Detect commitments about refunds, timelines, SLA guarantees.
    The system must not promise specific timelines, refund amounts, or SLA exceptions.

    Returns:
        {
            "status": "pass" | "block",
            "reason": str,
            "flagged_phrases": list[str]
        }

    Raises:
        NotImplementedError: Until implemented in Week 2 Day 4
    """
    raise NotImplementedError("TODO: Guardrail 4 (Tone/Scope) - implement Week 2 Day 4")


def check_confidence_floor(routing_decision: dict, threshold: float) -> dict:
    """
    Guardrail 5: Verify the routing threshold was actually applied before auto-responding.
    If a response was auto-generated but confidence was below threshold, escalate.

    Returns:
        {
            "status": "pass" | "escalate",
            "reason": str
        }

    Raises:
        NotImplementedError: Until implemented in Week 2 Day 4
    """
    raise NotImplementedError(
        "TODO: Guardrail 5 (Confidence Floor) - implement Week 2 Day 4"
    )


def run_guardrails(
    response: dict,
    ticket: dict,
    passages: list[dict],
    routing_decision: dict,
) -> dict:
    """
    Run all 5 guardrails on a response and return the combined result.

    Args:
        response: Output of generate.generate_response()
        ticket: Normalised ticket dict
        passages: Retrieved passages used for generation
        routing_decision: Output of route.route_ticket()

    Returns:
        {
            "overall_status": "pass" | "block" | "escalate",
            "action": "send_response" | "block_and_escalate" | "escalate",
            "pii": result of check_pii(),
            "grounding": result of check_grounding(),
            "injection": result of check_injection(),
            "tone_scope": result of check_tone_scope(),
            "confidence_floor": result of check_confidence_floor(),
            "blocked_by": list[str]  # names of guardrails that triggered
        }

    Raises:
        NotImplementedError: Until implemented in Week 2 Day 4
    """
    raise NotImplementedError(
        "TODO: implement run_guardrails() - Week 2 Day 4"
    )
