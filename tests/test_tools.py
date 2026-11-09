"""Unit tests for the external tools (network mocked)."""
import tools


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def test_search_literature_parses_results(monkeypatch):
    captured = {}

    def fake_get(url, params=None, timeout=None):
        captured["params"] = params
        return _FakeResponse({"docs": [
            {"title": "Candide", "author_name": ["Voltaire"]},
        ]})

    monkeypatch.setattr(tools.requests, "get", fake_get)
    out = tools.search_literature("espoir & joie")

    assert "Candide" in out and "Voltaire" in out
    # Query is passed via params so it is URL-encoded safely.
    assert captured["params"]["q"] == "espoir & joie"


def test_search_literature_handles_errors(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("network down")

    monkeypatch.setattr(tools.requests, "get", boom)
    out = tools.search_literature("x")
    assert "Erreur" in out


def test_search_web_links(monkeypatch):
    class FakeDDGS:
        def text(self, query, max_results=2):
            return [{"title": "Lire Candide", "href": "https://example.org"}]

    monkeypatch.setattr(tools, "DDGS", FakeDDGS)
    out = tools.search_web_links("Candide")
    assert "example.org" in out
