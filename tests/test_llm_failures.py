"""A11: rate limiting, provider timeout and exhausted credit are handled without crashing, and without sleeping for real in tests."""
import pytest
from src import llm


class _Resp:
    def __init__(self, text="ok"):
        self.choices = [type("C", (), {"message": type("M", (), {"content": text})()})()]
        self.usage = type("U", (), {"total_tokens": 5})()


class _HTTPError(Exception):
    def __init__(self, status, retry_after=None):
        super().__init__(f"HTTP {status}")
        self.status_code = status
        self.response = type("R", (), {"headers": {"retry-after": str(retry_after)} if retry_after is not None else {}})()


class _Client:
    def __init__(self, script):
        self.script, self.calls = list(script), 0
        self.chat = type("Ch", (), {"completions": self})()
    def create(self, **kw):
        self.calls += 1
        step = self.script.pop(0) if self.script else _Resp()
        if isinstance(step, Exception):
            raise step
        return step


@pytest.fixture
def provider(monkeypatch, tmp_path):
    slept = []
    monkeypatch.setattr(llm.time, "sleep", lambda s: slept.append(s))
    monkeypatch.setattr(llm, "CACHE_ENABLED", False)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    llm.reset_breaker()
    def install(script):
        c = _Client(script)
        monkeypatch.setattr(llm, "_client", lambda: c)
        return c
    install.slept = slept
    yield install
    llm.reset_breaker()


M = [{"role": "user", "content": "hi"}]


def test_rate_limit_waits_for_retry_after_then_succeeds(provider):
    c = provider([_HTTPError(429, retry_after=2)])
    assert llm.chat(M, temperature=0.1)["text"] == "ok"
    assert c.calls == 2 and any(s >= 2 for s in provider.slept), "should have waited the Retry-After time"


def test_daily_cap_429_fails_fast_instead_of_waiting_for_hours(provider):
    c = provider([_HTTPError(429, retry_after=7200)])
    with pytest.raises(llm.LLMUnavailable):
        llm.chat(M, temperature=0.1)
    assert c.calls == 1 and not any(s > 100 for s in provider.slept)


def test_timeouts_are_retried_then_become_unavailable_not_a_crash(provider):
    c = provider([TimeoutError("timed out")] * 10)
    with pytest.raises(llm.LLMUnavailable):
        llm.chat(M, temperature=0.1)
    assert c.calls == llm.MAX_RETRIES


def test_exhausted_credit_fails_fast_and_opens_the_breaker(provider):
    c = provider([_HTTPError(402)])
    with pytest.raises(llm.LLMUnavailable):
        llm.chat(M, temperature=0.1)
    assert c.calls == 1
    with pytest.raises(llm.LLMUnavailable):          # breaker open: no further provider calls
        llm.chat(M, temperature=0.1)
    assert c.calls == 1


def test_pacing_spaces_calls_to_the_configured_rate(provider, monkeypatch):
    """LLM_MAX_RPM=30 means at least 2 s between calls: the second call waits instead of firing straight into a rate limit."""
    clock = {"t": 100.0}
    monkeypatch.setattr(llm.time, "monotonic", lambda: clock["t"])
    monkeypatch.setattr(llm.time, "sleep", lambda s: (provider.slept.append(s), clock.__setitem__("t", clock["t"] + s)))
    monkeypatch.setattr(llm, "MAX_RPM", 30.0)
    monkeypatch.setitem(llm._pace_state, "last", 0.0)
    provider([])
    llm.chat(M, temperature=0.1)
    llm.chat(M, temperature=0.1)
    assert any(abs(s - 2.0) < 1e-6 for s in provider.slept), provider.slept
