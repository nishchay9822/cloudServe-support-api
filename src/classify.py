"""
Classification module — predicts intent and urgency with calibrated confidence score.
Satisfies acceptance criteria: A3 (every ticket classified with numeric confidence 0-1)

Intent classes (22 total): billing_inquiry, password_reset, api_error, deployment_issue,
performance_degradation, feature_request, onboarding_help, data_export, security_concern,
integration_question, account_management, refund_request, service_outage,
documentation_request, compliance_inquiry, sla_question, cancellation_request,
upgrade_request, bug_report, access_permission, audit_log_request, general_inquiry

Urgency levels: high, medium, low
"""
from typing import Optional

INTENT_CLASSES = [
    "billing_inquiry", "password_reset", "api_error", "deployment_issue",
    "performance_degradation", "feature_request", "onboarding_help", "data_export",
    "security_concern", "integration_question", "account_management", "refund_request",
    "service_outage", "documentation_request", "compliance_inquiry", "sla_question",
    "cancellation_request", "upgrade_request", "bug_report", "access_permission",
    "audit_log_request", "general_inquiry",
]

URGENCY_LEVELS = ["high", "medium", "low"]


def classify_ticket(ticket: dict, prompt_version: str = "PR-CL-01 v1.0") -> dict:
    """
    Classify a normalised ticket for intent and urgency.

    Args:
        ticket: Normalised ticket dict (output of ingest.normalize_ticket)
        prompt_version: Version string of the classification prompt used

    Returns:
        Classification dict with keys:
        - intent (str): one of INTENT_CLASSES
        - urgency (str): one of URGENCY_LEVELS
        - confidence (float): calibrated confidence score 0.0-1.0
        - alternatives (list): top-3 alternative intents with scores
        - prompt_version (str): prompt version used

    Note:
        Confidence MUST be calibrated — 80-90% confidence predictions should be
        correct ~85% of the time. Do not inflate confidence scores. Calibration
        check runs in Week 2 Day 5 evaluation gate.

    Raises:
        NotImplementedError: Until implemented in Week 2 Day 3
    """
    raise NotImplementedError("TODO: implement classify_ticket() - Week 2 Day 3")
