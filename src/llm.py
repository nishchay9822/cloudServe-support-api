"""
Shared LLM client (OpenRouter, OpenAI-compatible).

Design goals (A11 - fail gracefully):
- Never hang: per-call timeout.
- Retry transient failures (rate limit, timeout, 5xx) with exponential backoff.
- Circuit breaker: after repeated failures, stop calling the provider for a
  cool-down window so a provider outage does not make a run crawl.
- Missing API key or provider outage raises LLMUnavailable, which callers
  turn into an escalation. It never crashes the pipeline.
"""
import json
import os
import time
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

# Any OpenAI-compatible provider works. Defaults to OpenRouter. For Groq's free tier set:
#   LLM_BASE_URL=https://api.groq.com/openai/v1   LLM_API_KEY=<groq key>   MODEL_NAME=llama-3.1-8b-instant
# (Groq is untested here: no key was available. OpenRouter is the tested path.)
BASE_URL = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
TIMEOUT_S = float(os.getenv("LLM_TIMEOUT_S", "30"))
MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "3"))
BREAKER_THRESHOLD = int(os.getenv("LLM_BREAKER_THRESHOLD", "4"))
BREAKER_COOLDOWN_S = float(os.getenv("LLM_BREAKER_COOLDOWN_S", "30"))
PROVIDER_SORT = os.getenv("LLM_PROVIDER_SORT", "throughput")  # "", "latency" or "throughput"

_state = {"consecutive_failures": 0, "open_until": 0.0, "client": None, "client_key": None}
# Counters for the run report (calls, retries, failures, tokens, seconds spent waiting on the provider).
stats = {"calls": 0, "retries": 0, "failures": 0, "tokens": 0, "seconds": 0.0}


class LLMUnavailable(Exception):
    """The model provider cannot be used right now (no key, outage, rate limit)."""


def model_name() -> str:
    return os.getenv("MODEL_NAME", "meta-llama/llama-3.1-8b-instruct")


def _api_key() -> str:
    key = os.getenv("LLM_API_KEY") or os.getenv("OPENROUTER_API_KEY", "")
    if not key or key == "your_key_here":
        return ""
    return key


def _client():
    from openai import OpenAI

    key = _api_key()
    if _state["client"] is None or _state["client_key"] != key:
        _state["client"] = OpenAI(base_url=os.getenv("LLM_BASE_URL", BASE_URL), api_key=key, timeout=TIMEOUT_S, max_retries=0)
        _state["client_key"] = key
    return _state["client"]


# Response cache (the spec encourages caching: it saves free-tier allowance and makes runs reproducible).
# Only deterministic calls (temperature 0) are cached, keyed on model + messages + max_tokens, so changing a prompt or a model
# can never return an old answer. It is never consulted when no key is configured, so the provider-outage drill still shows no replies.
CACHE_ENABLED = os.getenv("LLM_CACHE", "1") == "1"
CACHE_PATH = os.getenv("LLM_CACHE_PATH", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage", "llm_cache.sqlite"))


def _cache_key(model: str, messages: list, max_tokens: int) -> str:
    import hashlib
    return hashlib.sha256(json.dumps([model, max_tokens, messages], sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def _cache_conn():
    import sqlite3
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    conn = sqlite3.connect(CACHE_PATH, timeout=30)
    conn.execute("CREATE TABLE IF NOT EXISTS llm_cache (k TEXT PRIMARY KEY, text TEXT NOT NULL)")
    return conn


def _cache_get(key: str) -> Optional[str]:
    try:
        with _cache_conn() as c:
            row = c.execute("SELECT text FROM llm_cache WHERE k=?", (key,)).fetchone()
        return row[0] if row else None
    except Exception:
        return None


def _cache_put(key: str, text: str) -> None:
    try:
        with _cache_conn() as c:
            c.execute("INSERT OR REPLACE INTO llm_cache VALUES (?,?)", (key, text))
    except Exception:
        pass


RATE_LIMIT_MAX_WAIT_S = float(os.getenv("LLM_RATE_LIMIT_MAX_WAIT_S", "60"))
RATE_LIMIT_MAX_WAITS = int(os.getenv("LLM_RATE_LIMIT_MAX_WAITS", "6"))


def _retry_after(e: Exception) -> Optional[float]:
    """Seconds the provider asks us to wait, from the Retry-After header (None if absent)."""
    try:
        return float(e.response.headers.get("retry-after"))
    except Exception:
        return None


def _extra_body(model: str) -> Optional[dict]:
    body: dict = {}
    if PROVIDER_SORT and "openrouter" in BASE_URL:
        body["provider"] = {"sort": PROVIDER_SORT}
    if "gpt-oss" in model and "groq" in os.getenv("LLM_BASE_URL", BASE_URL):
        body["reasoning_effort"] = "low"  # otherwise hidden reasoning eats the max_tokens budget
    return body or None


def reset_breaker() -> None:
    _state["consecutive_failures"] = 0
    _state["open_until"] = 0.0


def provider_host() -> str:
    """Host of the model provider in use (for the audit log); never includes keys."""
    from urllib.parse import urlparse
    return urlparse(os.getenv("LLM_BASE_URL", BASE_URL)).netloc or "unknown"


def is_available() -> bool:
    return bool(_api_key()) and time.time() >= _state["open_until"]


def chat(messages: list, max_tokens: int = 400, temperature: float = 0.0, model: Optional[str] = None) -> dict:
    """
    Call the model (default MODEL_NAME; `model` overrides, e.g. an independent judge).
    Returns {"text": str, "tokens": int}. Raises LLMUnavailable if the provider cannot be used.
    """
    if not _api_key():
        raise LLMUnavailable("OPENROUTER_API_KEY is not set")
    use_cache = CACHE_ENABLED and temperature == 0
    ckey = _cache_key(model or model_name(), messages, max_tokens) if use_cache else None
    if use_cache:
        hit = _cache_get(ckey)
        if hit is not None:
            stats["cache_hits"] = stats.get("cache_hits", 0) + 1
            return {"text": hit, "tokens": 0}
    if time.time() < _state["open_until"]:
        raise LLMUnavailable("circuit breaker open after repeated provider failures")

    last_err: Optional[Exception] = None
    attempt, rl_waits = -1, 0
    while attempt + 1 < MAX_RETRIES:
        attempt += 1
        t_call = time.time()
        if attempt or rl_waits:
            stats["retries"] += 1
        try:
            resp = _client().chat.completions.create(
                model=model or model_name(),
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                # Default OpenRouter routing measured at ~11 s median for a short reply; sorting providers by
                # throughput measured ~0.4 s (evaluation/time_llm.py). Same model, same weights.
                extra_body=_extra_body(model or model_name()),
            )
            text = (resp.choices[0].message.content or "").strip()
            tokens = getattr(getattr(resp, "usage", None), "total_tokens", 0) or 0
            _state["consecutive_failures"] = 0
            stats["calls"] += 1
            stats["tokens"] += int(tokens)
            stats["seconds"] += time.time() - t_call
            if use_cache and text:
                _cache_put(ckey, text)
            return {"text": text, "tokens": int(tokens)}
        except Exception as e:  # network, rate limit, 5xx, malformed response
            last_err = e
            stats["seconds"] += time.time() - t_call
            status = getattr(e, "status_code", None)
            if status in (400, 401, 402, 403, 404):  # not transient (bad request/key, NO CREDITS, forbidden): retrying cannot help
                last_err = e
                _state["open_until"] = time.time() + BREAKER_COOLDOWN_S if status in (401, 402) else _state["open_until"]
                break
            if status == 429:
                # Rate limit (e.g. free-tier tokens-per-minute). Honour Retry-After for short waits and do not
                # use up a normal retry; a long wait means a daily cap, which retrying cannot fix.
                wait = _retry_after(e)
                if wait is not None and wait <= RATE_LIMIT_MAX_WAIT_S and rl_waits < RATE_LIMIT_MAX_WAITS:
                    rl_waits += 1
                    attempt -= 1
                    time.sleep(wait + 0.5)
                    continue
                if wait is not None and wait > RATE_LIMIT_MAX_WAIT_S:
                    break
            time.sleep(min(2 ** attempt, 8))

    stats["failures"] += 1
    _state["consecutive_failures"] += 1
    if _state["consecutive_failures"] >= BREAKER_THRESHOLD:
        _state["open_until"] = time.time() + BREAKER_COOLDOWN_S
    code = getattr(last_err, "status_code", None)
    raise LLMUnavailable(f"provider call failed: {type(last_err).__name__}" + (f" (HTTP {code})" if code else ""))
