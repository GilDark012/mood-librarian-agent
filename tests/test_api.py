"""Integration tests for the API (LLM mocked)."""
from types import SimpleNamespace

import agent
import config


def _fake_completion(content):
    message = SimpleNamespace(content=content, tool_calls=None)
    choice = SimpleNamespace(message=message)
    usage = SimpleNamespace(total_tokens=42)
    return SimpleNamespace(choices=[choice], usage=usage)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_root_serves_ui(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "Bibliothécaire de l'Humeur" in r.text


def test_recommend_blocked(client):
    r = client.post("/recommend", json={"mood": "je veux mourir"})
    assert r.status_code == 200
    assert r.json()["status"] == "blocked"
    assert "3114" in r.json()["message"]


def test_recommend_success(client, monkeypatch):
    monkeypatch.setattr(
        agent.client.chat.completions,
        "create",
        lambda **kwargs: _fake_completion("Je te conseille Candide car c'est joyeux http://x"),
    )
    r = client.post("/recommend", json={"mood": "je me sens joyeux"})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert "disclaimer" in data
    assert data["metrics"]["total_tokens"] == 42


def test_empty_mood_rejected(client):
    r = client.post("/recommend", json={"mood": "   "})
    assert r.status_code == 422


def test_too_long_mood_rejected(client):
    r = client.post("/recommend", json={"mood": "x" * 5000})
    assert r.status_code == 422


def test_api_key_enforced_when_configured(client, monkeypatch):
    monkeypatch.setattr(config.settings, "api_key", "secret")
    # No header -> rejected.
    r = client.post("/recommend", json={"mood": "calme"})
    assert r.status_code == 401
    # Correct header -> passes auth (blocked path needs no LLM).
    r2 = client.post(
        "/recommend",
        json={"mood": "je veux mourir"},
        headers={"X-API-Key": "secret"},
    )
    assert r2.status_code == 200
    assert r2.json()["status"] == "blocked"
