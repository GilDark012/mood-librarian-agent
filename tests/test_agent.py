"""Unit tests for the agent loop's robustness."""
from types import SimpleNamespace

import agent


def _tool_call_response():
    tc = SimpleNamespace(
        id="call_1",
        function=SimpleNamespace(name="search_literature", arguments="{}"),
    )
    message = SimpleNamespace(content=None, tool_calls=[tc])
    return SimpleNamespace(choices=[SimpleNamespace(message=message)],
                           usage=SimpleNamespace(total_tokens=10))


def _text_response(text):
    message = SimpleNamespace(content=text, tool_calls=None)
    return SimpleNamespace(choices=[SimpleNamespace(message=message)],
                           usage=SimpleNamespace(total_tokens=5))


def test_forces_final_answer_when_loop_exhausts(monkeypatch):
    """If the model keeps calling tools (e.g. web search keeps failing), the
    agent must still return a real recommendation, not a 'interrupted' stub."""
    def fake_create(**kwargs):
        # The forced final call is made WITHOUT tools.
        if "tools" not in kwargs:
            return _text_response("Je te conseille 'Candide' de Voltaire, car il est léger.")
        return _tool_call_response()  # loop iterations: always ask for a tool

    monkeypatch.setattr(agent.client.chat.completions, "create", fake_create)
    monkeypatch.setattr(agent, "search_literature", lambda *a, **k: "Titre: Candide")
    monkeypatch.setattr(agent, "search_reading_link", lambda *a, **k: "Aucun lien disponible.")

    out = agent.agent_handler("je me sens joyeux")

    assert out["status"] == "success"
    assert "Candide" in out["recommendation"]
    assert "interrompue" not in out["recommendation"].lower()


def test_evaluate_response_rewards_link_and_justification():
    good = "**Candide** — Voltaire. Idéal car léger. 📖 Lire : http://example.org"
    assert agent.evaluate_response(good) >= 0.7
    assert agent.evaluate_response("") == 0.0
