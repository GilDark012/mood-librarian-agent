"""Aggregate, non-identifying usage statistics.

Counts only (requests, status breakdown, tokens, latency, rate-limit hits) —
never the content of user requests, keeping the no-persistence privacy stance.

Durable via Upstash Redis (REST) when configured; otherwise in-memory (reset on
restart). Recording never raises: a stats failure must not break a user request.
"""
import logging
import threading

import requests

from config import settings

logger = logging.getLogger(__name__)

_HASH = "stats"
_STATUSES = ("success", "blocked", "error")
_ENDPOINTS = ("recommend", "journey")


class _MemoryStore:
    def __init__(self) -> None:
        self._data: dict[str, int] = {}
        self._lock = threading.Lock()

    def incr_many(self, items: dict[str, int]) -> None:
        with self._lock:
            for key, amount in items.items():
                self._data[key] = self._data.get(key, 0) + amount

    def all(self) -> dict[str, int]:
        with self._lock:
            return dict(self._data)


class _UpstashStore:
    def __init__(self, url: str, token: str) -> None:
        self._url = url.rstrip("/")
        self._headers = {"Authorization": f"Bearer {token}"}

    def incr_many(self, items: dict[str, int]) -> None:
        commands = [["HINCRBY", _HASH, key, amount] for key, amount in items.items()]
        requests.post(f"{self._url}/pipeline", json=commands, headers=self._headers, timeout=4)

    def all(self) -> dict[str, int]:
        res = requests.post(f"{self._url}", json=["HGETALL", _HASH], headers=self._headers, timeout=4)
        res.raise_for_status()
        flat = res.json().get("result") or []
        return {flat[i]: int(flat[i + 1]) for i in range(0, len(flat) - 1, 2)}


def _make_store():
    if settings.upstash_redis_rest_url and settings.upstash_redis_rest_token:
        return _UpstashStore(settings.upstash_redis_rest_url, settings.upstash_redis_rest_token)
    return _MemoryStore()


_store = _make_store()


def record(endpoint: str, status: str, tokens: int = 0, latency_ms: int = 0) -> None:
    """Record one request's aggregate metrics. Never raises."""
    items = {f"req:{endpoint}": 1, f"st:{endpoint}:{status}": 1}
    if tokens:
        items["tokens"] = int(tokens)
    if latency_ms:
        items["latency_ms_sum"] = int(latency_ms)
        items["latency_count"] = 1
    try:
        _store.incr_many(items)
    except Exception as e:
        logger.warning("stats record failed: %s", e)


def record_rate_limited() -> None:
    try:
        _store.incr_many({"rate_limited": 1})
    except Exception as e:
        logger.warning("stats rate-limit record failed: %s", e)


def snapshot() -> dict:
    """Return the aggregate stats. Never raises."""
    try:
        data = _store.all()
    except Exception as e:
        logger.warning("stats snapshot failed: %s", e)
        data = {}

    tokens = data.get("tokens", 0)
    lat_sum = data.get("latency_ms_sum", 0)
    lat_n = data.get("latency_count", 0)
    return {
        "durable": isinstance(_store, _UpstashStore),
        "requests": {ep: data.get(f"req:{ep}", 0) for ep in _ENDPOINTS},
        "status": {
            ep: {s: data.get(f"st:{ep}:{s}", 0) for s in _STATUSES} for ep in _ENDPOINTS
        },
        "rate_limited": data.get("rate_limited", 0),
        "blocked_total": sum(data.get(f"st:{ep}:blocked", 0) for ep in _ENDPOINTS),
        "total_tokens": tokens,
        "estimated_cost_usd": round(tokens / 1_000_000 * settings.cost_per_mtoken_usd, 4),
        "avg_latency_ms": round(lat_sum / lat_n) if lat_n else 0,
    }
