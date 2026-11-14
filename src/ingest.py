"""
Ingest: normalise tickets from the four channels into one internal representation.
Satisfies A2.

The data uses the channel names: email, chat, docs_comment, forum.
'api_comments' (the name used in the brief) is accepted as an alias.
Ground-truth fields (labels, history) are deliberately NOT carried into the
normalised ticket: downstream components must predict, not read answers.
"""
import json
import re
from typing import Optional

SUPPORTED_CHANNELS = ["email", "chat", "docs_comment", "forum"]
CHANNEL_ALIASES = {"api_comments": "docs_comment", "api_docs_comment": "docs_comment",
                   "docs": "docs_comment", "community_forum": "forum", "live_chat": "chat"}

_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _clean(value) -> str:
    if value is None:
        return ""
    text = _CONTROL.sub("", str(value))
    return re.sub(r"[ \t]+", " ", text).strip()


def canonical_channel(channel) -> str:
    if not isinstance(channel, str) or not channel.strip():
        raise ValueError(f"Unsupported channel: {channel!r}. Must be one of {SUPPORTED_CHANNELS}")
    ch = channel.strip().lower()
    ch = CHANNEL_ALIASES.get(ch, ch)
    if ch not in SUPPORTED_CHANNELS:
        raise ValueError(f"Unsupported channel: {channel!r}. Must be one of {SUPPORTED_CHANNELS}")
    return ch


def normalize_ticket(raw: dict, channel: Optional[str] = None) -> dict:
    """
    Normalise a raw ticket. `channel` overrides raw['channel'] when given.

    Raises ValueError for non-dict input or an unsupported channel.
    Missing optional fields get safe defaults so one malformed ticket
    cannot stop a run.
    """
    if not isinstance(raw, dict):
        raise ValueError("ticket must be a JSON object")
    ch = canonical_channel(channel if channel is not None else raw.get("channel"))

    body = _clean(raw.get("body"))
    subject = _clean(raw.get("subject"))
    return {
        "ticket_id": _clean(raw.get("ticket_id")) or "UNKNOWN",
        "channel": ch,
        "subject": subject,
        "body": body,
        "received_at": _clean(raw.get("received_at")),
        "customer_id": _clean(raw.get("customer_id")),
        "customer_name": _clean(raw.get("customer_name")),  # kept only so the PII guardrail can detect leakage
        "customer_tier": (_clean(raw.get("customer_tier")) or "standard").lower(),
        "customer_region": _clean(raw.get("customer_region")) or "unknown",
        "language_fluency": (_clean(raw.get("language_fluency")) or "fluent").lower(),
        "text": (subject + "\n" + body).strip(),
        "is_empty": not (subject or body),
        # The spec asks ingest to preserve the original text and channel: the cleaned fields above are what the pipeline uses,
        # the untouched originals travel with the ticket. Ground-truth fields (labels, history) are deliberately NOT copied.
        "original": {"channel": raw.get("channel"), "subject": raw.get("subject"), "body": raw.get("body")},
    }


def load_tickets(filepath: str) -> list:
    """Load tickets from a JSON file (a list of ticket objects)."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = data.get("tickets", [])
    if not isinstance(data, list):
        raise ValueError("ticket file must contain a JSON list")
    return data
