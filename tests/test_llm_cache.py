"""Response cache: identical deterministic calls are served locally; changes bust it; no key means no cache and no reply."""
import pytest
from src import llm


class _Resp:
    def __init__(self, text):
        self.choices = [type("C", (), {"message": type("M", (), {"content": text})()})()]
        self.usage = type("U", (), {"total_tokens": 7})()


class _Client:
    def __init__(self):
        self.calls = 0
        self.chat = type("Ch", (), {"completions": self})()
    def create(self, **kw):
        self.calls += 1
        return _Resp(f"answer {self.calls}")


@pytest.fixture
def fake_provider(monkeypatch, tmp_path):
    c = _Client()
    monkeypatch.setattr(llm, "_client", lambda: c)
    monkeypatch.setattr(llm, "CACHE_PATH", str(tmp_path / "cache.sqlite"))
    monkeypatch.setattr(llm, "CACHE_ENABLED", True)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    llm.reset_breaker()
    return c


M = [{"role": "user", "content": "hello"}]


def test_second_identical_call_is_served_from_cache(fake_provider):
    a = llm.chat(M, max_tokens=10, temperature=0)
    b = llm.chat(M, max_tokens=10, temperature=0)
    assert fake_provider.calls == 1 and a["text"] == b["text"] and b["tokens"] == 0


def test_changed_prompt_or_model_is_a_cache_miss(fake_provider):
    llm.chat(M, max_tokens=10, temperature=0)
    llm.chat([{"role": "user", "content": "hello!"}], max_tokens=10, temperature=0)
    llm.chat(M, max_tokens=10, temperature=0, model="other/model")
    assert fake_provider.calls == 3


def test_non_deterministic_calls_are_never_cached(fake_provider):
    llm.chat(M, max_tokens=10, temperature=0.7)
    llm.chat(M, max_tokens=10, temperature=0.7)
    assert fake_provider.calls == 2


def test_no_key_means_unavailable_even_if_the_answer_is_cached(fake_provider, monkeypatch):
    llm.chat(M, max_tokens=10, temperature=0)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.setattr(llm, "_api_key", lambda: "")
    with pytest.raises(llm.LLMUnavailable):
        llm.chat(M, max_tokens=10, temperature=0)
