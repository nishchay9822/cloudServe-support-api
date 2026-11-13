"""
Decision log (SQLite). Satisfies A8.

One row per processed ticket, written even when the ticket failed or was escalated,
so that count_decisions(run_id) can be reconciled against tickets processed.
A second table holds resolution records (the compounding 'resolution graph').
"""
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Optional


def get_db_path() -> str:
    url = os.getenv("DATABASE_URL", "sqlite:///./storage/decisions.db")
    return url.replace("sqlite:///", "", 1) if url.startswith("sqlite:///") else "./storage/decisions.db"


def _connect() -> sqlite3.Connection:
    path = get_db_path()
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    conn = sqlite3.connect(path, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


_JSON_FIELDS = ("alternatives", "sources_used", "guardrail_results", "requirement_ids", "extra")


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS decisions (
                decision_id TEXT PRIMARY KEY,
                run_id TEXT,
                timestamp TEXT NOT NULL,
                ticket_id TEXT NOT NULL,
                stage TEXT NOT NULL,
                input_summary TEXT,
                model_name TEXT,
                model_version TEXT,
                prediction_value TEXT,
                prediction_confidence REAL,
                alternatives TEXT,
                sources_used TEXT,
                threshold_applied REAL,
                action_taken TEXT,
                reason TEXT,
                guardrail_results TEXT,
                prompt_version TEXT,
                requirement_ids TEXT,
                extra TEXT
            )"""
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_dec_run ON decisions(run_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_dec_ticket ON decisions(ticket_id)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS resolution_records (
                record_id TEXT PRIMARY KEY,
                run_id TEXT,
                timestamp TEXT NOT NULL,
                ticket_id TEXT NOT NULL,
                intent TEXT,
                doc_ids TEXT,
                confidence REAL,
                customer_tier TEXT,
                language_fluency TEXT
            )"""
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                feedback_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                ticket_id TEXT NOT NULL,
                decision_id TEXT,
                original_decision TEXT,
                original_intent TEXT,
                corrected_intent TEXT,
                corrected_urgency TEXT,
                corrected_route TEXT,
                resolved INTEGER,
                note TEXT,
                applied_to_index INTEGER DEFAULT 0
            )"""
        )


def log_decision(decision: dict) -> str:
    """Write one decision. Returns decision_id. Raises on a missing ticket_id."""
    if not decision.get("ticket_id"):
        raise ValueError("decision requires a ticket_id")
    init_db()
    did = decision.get("decision_id") or str(uuid.uuid4())
    model = decision.get("model") or {}
    pred = decision.get("prediction") or {}
    row = {
        "decision_id": did,
        "run_id": decision.get("run_id"),
        "timestamp": decision.get("timestamp") or datetime.now(timezone.utc).isoformat(),
        "ticket_id": decision["ticket_id"],
        "stage": decision.get("stage", "final"),
        "input_summary": (decision.get("input_summary") or "")[:300],
        "model_name": model.get("name"),
        "model_version": model.get("version"),
        "prediction_value": pred.get("value"),
        "prediction_confidence": pred.get("confidence"),
        "alternatives": json.dumps(decision.get("alternatives") or []),
        "sources_used": json.dumps(decision.get("sources_used") or []),
        "threshold_applied": decision.get("threshold_applied"),
        "action_taken": decision.get("action_taken"),
        "reason": decision.get("reason"),
        "guardrail_results": json.dumps(decision.get("guardrail_results") or {}, default=str),
        "prompt_version": decision.get("prompt_version"),
        "requirement_ids": json.dumps(decision.get("requirement_ids") or []),
        "extra": json.dumps(decision.get("extra") or {}, default=str),
    }
    cols = ", ".join(row)
    marks = ", ".join(":" + k for k in row)
    with _connect() as conn:
        conn.execute(f"INSERT OR REPLACE INTO decisions ({cols}) VALUES ({marks})", row)
    return did


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for f in _JSON_FIELDS:
        if d.get(f):
            try:
                d[f] = json.loads(d[f])
            except (TypeError, ValueError):
                pass
    return d


def get_decision(decision_id: str) -> Optional[dict]:
    init_db()
    with _connect() as conn:
        row = conn.execute("SELECT * FROM decisions WHERE decision_id = ?", (decision_id,)).fetchone()
    return _row_to_dict(row) if row else None


def get_decisions_for_ticket(ticket_id: str) -> list:
    init_db()
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM decisions WHERE ticket_id = ? ORDER BY timestamp", (ticket_id,)).fetchall()
    return [_row_to_dict(r) for r in rows]


def count_decisions(ticket_id: Optional[str] = None, run_id: Optional[str] = None) -> int:
    init_db()
    q, args = "SELECT COUNT(*) FROM decisions WHERE 1=1", []
    if ticket_id:
        q += " AND ticket_id = ?"; args.append(ticket_id)
    if run_id:
        q += " AND run_id = ?"; args.append(run_id)
    with _connect() as conn:
        return int(conn.execute(q, args).fetchone()[0])


def log_resolution(record: dict) -> str:
    """Store a reusable resolution record (no customer identity is stored)."""
    init_db()
    rid = str(uuid.uuid4())
    with _connect() as conn:
        conn.execute(
            "INSERT INTO resolution_records VALUES (?,?,?,?,?,?,?,?,?)",
            (rid, record.get("run_id"), datetime.now(timezone.utc).isoformat(), record["ticket_id"],
             record.get("intent"), json.dumps(record.get("doc_ids") or []), record.get("confidence"),
             record.get("customer_tier"), record.get("language_fluency")),
        )
    return rid


def count_resolutions(run_id: Optional[str] = None) -> int:
    init_db()
    with _connect() as conn:
        if run_id:
            return int(conn.execute("SELECT COUNT(*) FROM resolution_records WHERE run_id = ?", (run_id,)).fetchone()[0])
        return int(conn.execute("SELECT COUNT(*) FROM resolution_records").fetchone()[0])


def log_feedback(fb: dict) -> str:
    init_db()
    fid = str(uuid.uuid4())
    with _connect() as conn:
        conn.execute(
            "INSERT INTO feedback VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (fid, datetime.now(timezone.utc).isoformat(), fb["ticket_id"], fb.get("decision_id"), fb.get("original_decision"),
             fb.get("original_intent"), fb.get("corrected_intent"), fb.get("corrected_urgency"), fb.get("corrected_route"),
             None if fb.get("resolved") is None else int(bool(fb["resolved"])), (fb.get("note") or "")[:500],
             int(bool(fb.get("applied_to_index")))))
    return fid


def feedback_summary() -> dict:
    init_db()
    with _connect() as conn:
        q = lambda sql: conn.execute(sql).fetchone()[0]
        return {"total": q("SELECT COUNT(*) FROM feedback"),
                "intent_corrections": q("SELECT COUNT(*) FROM feedback WHERE corrected_intent IS NOT NULL AND corrected_intent != COALESCE(original_intent,'')"),
                "route_corrections": q("SELECT COUNT(*) FROM feedback WHERE corrected_route IS NOT NULL AND corrected_route != COALESCE(original_decision,'')"),
                "applied_to_index": q("SELECT COUNT(*) FROM feedback WHERE applied_to_index = 1"),
                "auto_replies_humans_say_should_escalate": q("SELECT COUNT(*) FROM feedback WHERE original_decision='auto_respond' AND corrected_route='escalate'")}

