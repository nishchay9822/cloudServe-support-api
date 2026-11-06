"""
Tests for the ingest module.
Run with: pytest tests/test_ingest.py -v

These tests define the expected behaviour of ingest.normalize_ticket().
Tests marked xfail WILL FAIL until Week 2 Day 1 when the function is implemented.
That is expected — tests exist to guide implementation, not to pass before coding starts.
"""
import pytest
from src.ingest import normalize_ticket, SUPPORTED_CHANNELS


class TestSupportedChannels:
    """Tests for the channel constants."""

    def test_exactly_four_channels(self):
        """Should have exactly 4 supported channels."""
        assert len(SUPPORTED_CHANNELS) == 4

    def test_all_expected_channels_present(self):
        """All four channel names must be present."""
        assert "email" in SUPPORTED_CHANNELS
        assert "chat" in SUPPORTED_CHANNELS
        assert "api_comments" in SUPPORTED_CHANNELS
        assert "forum" in SUPPORTED_CHANNELS


class TestNormalizeTicketValidation:
    """Tests that run immediately (do not require implementation)."""

    def test_rejects_unsupported_channel(self):
        """normalize_ticket should raise ValueError for unknown channels."""
        with pytest.raises(ValueError, match="Unsupported channel"):
            normalize_ticket({}, "telegram")

    def test_rejects_empty_channel_string(self):
        """normalize_ticket should raise ValueError for empty string channel."""
        with pytest.raises(ValueError):
            normalize_ticket({}, "")

    def test_rejects_none_channel(self):
        """normalize_ticket should raise ValueError for None channel."""
        with pytest.raises((ValueError, TypeError)):
            normalize_ticket({}, None)


class TestNormalizeTicketImplementation:
    """Tests that require the full implementation — marked xfail until Week 2 Day 1."""

    @pytest.mark.xfail(reason="Not implemented until Week 2 Day 1", strict=False)
    def test_normalizes_email_ticket(self):
        """Email ticket should normalise to standard schema."""
        raw = {
            "ticket_id": "DEV-0001",
            "channel": "email",
            "subject": "Can't log in",
            "body": "I keep getting invalid credential errors when I try to log in.",
            "received_at": "2024-01-15T09:00:00Z",
            "customer_id": "CUST-001",
            "customer_tier": "enterprise",
            "customer_region": "NA",
            "language_fluency": "fluent",
        }
        result = normalize_ticket(raw, "email")
        assert result["ticket_id"] == "DEV-0001"
        assert result["channel"] == "email"
        assert "body" in result
        assert "customer_tier" in result
        assert result["customer_tier"] == "enterprise"

    @pytest.mark.xfail(reason="Not implemented until Week 2 Day 1", strict=False)
    def test_normalizes_chat_ticket(self):
        """Chat ticket should normalise to same schema as email."""
        raw = {
            "ticket_id": "DEV-0002",
            "channel": "chat",
            "subject": "",
            "body": "my deployment keeps dying",
            "received_at": "2024-01-15T10:00:00Z",
            "customer_id": "CUST-002",
            "customer_tier": "standard",
            "customer_region": "EU",
            "language_fluency": "non-fluent",
        }
        result = normalize_ticket(raw, "chat")
        assert result["channel"] == "chat"
        assert result["language_fluency"] == "non-fluent"

    @pytest.mark.xfail(reason="Not implemented until Week 2 Day 1", strict=False)
    def test_normalizes_api_comments_ticket(self):
        """API comments ticket should normalise to standard schema."""
        raw = {
            "ticket_id": "DEV-0003",
            "channel": "api_comments",
            "subject": "Rate limit question",
            "body": "What is the rate limit for the /ingest endpoint?",
            "received_at": "2024-01-15T11:00:00Z",
            "customer_id": "CUST-003",
            "customer_tier": "business",
            "customer_region": "APAC",
            "language_fluency": "fluent",
        }
        result = normalize_ticket(raw, "api_comments")
        assert result["channel"] == "api_comments"

    @pytest.mark.xfail(reason="Not implemented until Week 2 Day 1", strict=False)
    def test_normalizes_forum_ticket(self):
        """Forum ticket should normalise to standard schema."""
        raw = {
            "ticket_id": "DEV-0004",
            "channel": "forum",
            "subject": "Integration help",
            "body": "Has anyone integrated with Salesforce?",
            "received_at": "2024-01-15T12:00:00Z",
            "customer_id": "CUST-004",
            "customer_tier": "standard",
            "customer_region": "LATAM",
            "language_fluency": "non-fluent",
        }
        result = normalize_ticket(raw, "forum")
        assert result["channel"] == "forum"

    @pytest.mark.xfail(reason="Not implemented until Week 2 Day 1", strict=False)
    def test_all_four_channels_produce_same_schema(self):
        """All 4 channels should produce normalised output with the same keys."""
        required_keys = {
            "ticket_id", "channel", "subject", "body", "received_at",
            "customer_id", "customer_tier", "customer_region", "language_fluency",
        }
        for channel in SUPPORTED_CHANNELS:
            raw = {
                "ticket_id": f"TEST-{channel}",
                "channel": channel,
                "subject": "test subject",
                "body": "test body text",
                "received_at": "2024-01-15T09:00:00Z",
                "customer_id": "CUST-TEST",
                "customer_tier": "standard",
                "customer_region": "NA",
                "language_fluency": "fluent",
            }
            result = normalize_ticket(raw, channel)
            for key in required_keys:
                assert key in result, (
                    f"Missing required key '{key}' in result for channel '{channel}'"
                )
