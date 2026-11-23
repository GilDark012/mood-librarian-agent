"""Unit tests for the aggregate statistics store (in-memory backend)."""
import stats


def test_record_and_snapshot(monkeypatch):
    monkeypatch.setattr(stats, "_store", stats._MemoryStore())

    stats.record("recommend", "success", tokens=100, latency_ms=2000)
    stats.record("recommend", "blocked")
    stats.record("journey", "success", tokens=50, latency_ms=4000)
    stats.record_rate_limited()

    snap = stats.snapshot()
    assert snap["durable"] is False
    assert snap["requests"] == {"recommend": 2, "journey": 1}
    assert snap["status"]["recommend"]["success"] == 1
    assert snap["status"]["recommend"]["blocked"] == 1
    assert snap["status"]["journey"]["success"] == 1
    assert snap["rate_limited"] == 1
    assert snap["blocked_total"] == 1
    assert snap["total_tokens"] == 150
    assert snap["avg_latency_ms"] == 3000  # (2000 + 4000) / 2


def test_record_never_raises_on_backend_error(monkeypatch):
    class Boom:
        def incr_many(self, items):
            raise RuntimeError("down")

        def all(self):
            raise RuntimeError("down")

    monkeypatch.setattr(stats, "_store", Boom())
    # Must not raise even though the backend fails.
    stats.record("recommend", "success", tokens=10)
    snap = stats.snapshot()
    assert snap["total_tokens"] == 0
