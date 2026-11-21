"""Unit tests for the external tools (network mocked)."""
import tools


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def test_search_manga_parses_and_ranks_by_popularity(monkeypatch):
    def fake_get(url, params=None, timeout=None):
        return _FakeResponse({"data": [
            {"title": "Obscure", "members": 50, "authors": [{"name": "X"}],
             "demographics": [{"name": "Shounen"}], "genres": [{"name": "Action"}],
             "themes": [], "score": 6.5, "scored_by": 40,
             "url": "https://myanimelist.net/manga/999", "synopsis": "obscure"},
            {"title": "Monster", "members": 500000, "authors": [{"name": "Urasawa, Naoki"}],
             "demographics": [{"name": "Seinen"}], "genres": [{"name": "Mystery"}],
             "themes": [{"name": "Psychological"}], "score": 9.0, "scored_by": 200000,
             "url": "https://myanimelist.net/manga/1", "synopsis": "A thriller."},
        ]})

    monkeypatch.setattr(tools.requests, "get", fake_get)
    out = tools.search_manga("thriller psychologique")
    assert "Monster" in out and "Seinen" in out and "9.0" in out
    assert "Urasawa, Naoki" in out
    # Popular title ranked before the obscure one.
    assert out.index("Monster") < out.index("Obscure")


def test_search_manga_handles_empty(monkeypatch):
    monkeypatch.setattr(tools.requests, "get", lambda *a, **k: _FakeResponse({"data": []}))
    assert "Aucun manga" in tools.search_manga("zzzz")


def test_search_literature_parses_results(monkeypatch):
    captured = {}

    def fake_get(url, params=None, timeout=None):
        captured["params"] = params
        return _FakeResponse({"docs": [
            {
                "title": "Candide",
                "author_name": ["Voltaire"],
                "first_publish_year": 1759,
                "key": "/works/OL123W",
            },
        ]})

    monkeypatch.setattr(tools.requests, "get", fake_get)
    out = tools.search_literature("espoir & joie")

    assert "Candide" in out and "Voltaire" in out
    assert "1759" in out
    assert "openlibrary.org/works/OL123W" in out
    # Query is passed via params so it is URL-encoded safely.
    assert captured["params"]["q"] == "espoir & joie"


def test_search_literature_handles_errors(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("network down")

    monkeypatch.setattr(tools.requests, "get", boom)
    out = tools.search_literature("x")
    assert "Erreur" in out


def test_search_reading_link_public_domain(monkeypatch):
    def fake_get(url, params=None, timeout=None):
        return _FakeResponse({"docs": [
            {
                "title": "Frankenstein",
                "key": "/works/OL450063W",
                "ia": ["frankenstein00shel"],
                "ebook_access": "public",
            },
        ]})

    monkeypatch.setattr(tools.requests, "get", fake_get)
    out = tools.search_reading_link("Frankenstein")
    assert "archive.org/details/frankenstein00shel" in out
    assert "Lecture gratuite" in out


def test_search_reading_link_no_ebook_falls_back_to_reference(monkeypatch):
    def fake_get(url, params=None, timeout=None):
        return _FakeResponse({"docs": [
            {"title": "Roman récent", "key": "/works/OL9W", "ebook_access": "no_ebook"},
        ]})

    monkeypatch.setattr(tools.requests, "get", fake_get)
    out = tools.search_reading_link("Roman récent")
    assert "openlibrary.org/works/OL9W" in out
