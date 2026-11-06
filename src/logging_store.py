"""
Decision logging module — writes every automated decision to SQLite with full schema.
Satisfies acceptance criteria: A8 (every automated decision written to persistent log)

CRITICAL: The log must cover ALL processed tickets, including failures and escalations.
A8 is checked by reconciling: count_decisions() == total tickets processed.
A ticket that failed or was escalated must still be logged.
"""
import os
import json
import sqlite3
import uuid
from datetime import datetime
from typing import Optional

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./storage/decisions.db")


def get_db_path() -> str:
    """Extract the file path from the DATABASE_URL environment variable."""
    if DATABASE_URL.startswith("sqlite:///"):
        return DATABASE_URL.replace("sqlite:///", "")
    return "./storage/decisions.db"


def init_db() -> None:
    """
    Initialize the SQLite database and create the decisions table if it does not exist.
    Call this once at application startup.

    The schema matches the required decision log JSON schema from Governance_Framework.docx.
    """
    db_path = get_db_path()
    parent = os.path.dirname(db_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS decisions (
            decision_id        TEXT PRIMARY KEY,
            timestamp          TEXT NOT NULL,
            ticket_id          TEXT NOT NULL,
            stage              TEXT NOT NULL,
            input_summary      TEXT,
            model_name         TEXT,
            model_version      TEXT,
            prediction_value   TEXT,
            prediction_confidence REAL,
            alternatives       TEXT,
            sources_used       TEXT,
            threshold_applied  REAL,
            action_taken       TEXT,
            reason             TEXT,
            guardrail_results  TEXT,
            prompt_version     TEXT,
            requirement_ids    TEXT,
            raw_decision       TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def log_decision(decision: dict) -> str:
    """
    Write a decision to the persistent log.

    Args:
        decision: Decision dict matching the required schema:
            {
                "decision_id":      str  (auto-generated if absent),
                "timestamp":        str  (ISO 8601),
                "ticket_id":        str,
                "stage":            str  (e.g. 'classify', 'route', 'generate', 'guardrail'),
                "input_summary":    str,
                "model":            {"name": str, "version": str},
                "prediction":       {"value": str, "confidence": float},
                "alternatives":     [{"value": str, "confidence": float}, ...],
                "sources_used":     [{"doc_id": str, "score": float}, ...],
                "threshold_applied": float,
                "action_taken":     str,
                "reason":           str,
                "guardrail_results":{"pii": dict, "grounding": dict, "tone": dict},
                "prompt_version":   str,
                "requirement_ids":  [str, ...]
            }

    Returns:
        decision_id (str)

    Raises:
        NotImplementedError: Until implemented in Week 2 Day 3
    """
    raise NotImplementedError("TODO: implement log_decision() - Week 2 Day 3")


def get_decision(decision_id: str) -> Optional[dict]:
    """
    Retrieve a single decision from the log by its ID.

    Returns:
        Decision dict if found, None if not found.

    Raises:
        NotImplementedError: Until implemented in Week 2 Day 3
    """
    raise NotImplementedError("TODO: implement get_decision() - Week 2 Day 3")


def count_decisions(ticket_id: Optional[str] = None) -> int:
    """
    Count total decisions logged, optionally filtered by ticket_id.

    Used for A8 reconciliation:
        assert count_decisions() == total_tickets_processed

    Returns:
        Integer count of decision log entries.

    Raises:
        NotImplementedError: Until implemented in Week 2 Day 3
    """
    raise NotImplementedError("TODO: implement count_decisions() - Week 2 Day 3")
