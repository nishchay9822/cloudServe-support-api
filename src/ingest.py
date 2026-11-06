"""
Ingest module — normalises tickets from 4 channels into one internal representation.
Satisfies acceptance criteria: A2 (all 4 channels ingested and normalised)
"""
from typing import Optional
import json
from datetime import datetime

SUPPORTED_CHANNELS = ["email", "chat", "api_comments", "forum"]


def normalize_ticket(raw: dict, channel: str) -> dict:
    """
    Normalise a raw ticket from any channel into a standard internal representation.

    Args:
        raw: Raw ticket dictionary as loaded from JSON
        channel: One of 'email', 'chat', 'api_comments', 'forum'

    Returns:
        Normalised ticket dict with keys:
        ticket_id, channel, subject, body, received_at,
        customer_id, customer_tier, customer_region, language_fluency

    Raises:
        ValueError: If channel is not supported
        NotImplementedError: Until implemented in Week 2 Day 1
    """
    if channel not in SUPPORTED_CHANNELS:
        raise ValueError(
            f"Unsupported channel: '{channel}'. Must be one of {SUPPORTED_CHANNELS}"
        )
    raise NotImplementedError("TODO: implement normalize_ticket() - Week 2 Day 1")


def load_tickets(filepath: str) -> list[dict]:
    """
    Load tickets from a JSON file.

    Args:
        filepath: Path to a JSON file containing a list of ticket dicts

    Returns:
        List of raw ticket dicts

    Raises:
        FileNotFoundError: If filepath does not exist
    """
    with open(filepath, "r") as f:
        return json.load(f)
