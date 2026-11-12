"""A2: tickets from all four channels normalise to one representation."""
import pytest

from src.ingest import SUPPORTED_CHANNELS, load_tickets, normalize_ticket

RAW = {"ticket_id": "T-1", "channel": "email", "subject": " Cannot log in ", "body": "Invalid credentials\x00 on login",
       "received_at": "2026-05-23T22:43:00Z", "customer_id": "CUST-1", "customer_name": "Ada Lovelace",
       "customer_tier": "Enterprise", "customer_region": "europe", "language_fluency": "fluent",
       "labels": {"intent": "x"}, "history": {"escalated": True}}
REQUIRED = {"ticket_id", "channel", "subject", "body", "received_at", "customer_id", "customer_tier",
            "customer_region", "language_fluency"}


def test_four_channels_supported():
    assert SUPPORTED_CHANNELS == ["email", "chat", "docs_comment", "forum"]


@pytest.mark.parametrize("channel", ["email", "chat", "docs_comment", "forum"])
def test_every_channel_gives_the_same_schema(channel):
    out = normalize_ticket({**RAW, "channel": channel})
    assert REQUIRED <= set(out)
    assert out["channel"] == channel


def test_api_comments_alias_maps_to_docs_comment():
    assert normalize_ticket(RAW, "api_comments")["channel"] == "docs_comment"


def test_ground_truth_is_not_carried_into_the_normalised_ticket():
    out = normalize_ticket(RAW)
    assert "labels" not in out and "history" not in out


def test_cleaning_and_defaults():
    out = normalize_ticket(RAW)
    assert out["subject"] == "Cannot log in" and "\x00" not in out["body"]
    assert out["customer_tier"] == "enterprise"
    sparse = normalize_ticket({"ticket_id": "T-2", "channel": "chat"})
    assert sparse["body"] == "" and sparse["customer_tier"] == "standard" and sparse["is_empty"] is True


@pytest.mark.parametrize("bad", ["telegram", "", None, 5])
def test_unsupported_channel_rejected(bad):
    with pytest.raises(ValueError):
        normalize_ticket({"ticket_id": "T"}, bad)


def test_non_dict_rejected():
    with pytest.raises(ValueError):
        normalize_ticket("not a ticket", "email")


def test_load_tickets_reads_a_list(tmp_path):
    p = tmp_path / "t.json"
    p.write_text('[{"ticket_id": "A"}, {"ticket_id": "B"}]')
    assert [t["ticket_id"] for t in load_tickets(str(p))] == ["A", "B"]
