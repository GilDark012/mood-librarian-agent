"""Unit tests for the agent loop's robustness."""
from types import SimpleNamespace

import agent


def _tool_call_response():
    tc = SimpleNamespace(
        id="call_1",
        function=SimpleNamespace(name="search_manga", arguments="{}"),
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
            return _text_response("**Naruto** — Masashi Kishimoto · Shōnen. À lire pour son cœur.")
        return _tool_call_response()  # loop iterations: always ask for a tool

    monkeypatch.setattr(agent.client.chat.completions, "create", fake_create)
    monkeypatch.setattr(agent, "search_manga", lambda *a, **k: "Titre: Naruto | Démographie: Shounen")

    out = agent.agent_handler("je me sens motivé")

    assert out["status"] == "success"
    assert "Naruto" in out["recommendation"]
    assert "interrompue" not in out["recommendation"].lower()


def test_evaluate_response_rewards_link_and_justification():
    good = "**Candide** — Voltaire. Idéal car léger. 📖 Lire : http://example.org"
    assert agent.evaluate_response(good) >= 0.7
    assert agent.evaluate_response("") == 0.0


def test_journey_handler_composes_pathway(monkeypatch):
    monkeypatch.setattr(
        agent.client.chat.completions, "create",
        lambda **kwargs: _text_response(
            "**Étape 1 — Accueillir**\n**Mushishi** — Urushibara · Seinen · ⭐ 8.7/10\n"
            "📖 Fiche : https://myanimelist.net/manga.php?q=Mushishi"
        ),
    )
    out = agent.journey_handler("je me sens triste", "je veux de l'espoir")
    assert out["status"] == "success"
    assert "Mushishi" in out["journey"]
    assert "myanimelist" in out["journey"]


def test_journey_blocks_crisis_in_desired_mood():
    # Safety must check the desired-mood field too; short-circuits before any LLM call.
    out = agent.journey_handler("je vais bien", "je veux en finir")
    assert out["status"] == "blocked"
    assert "3114" in out["message"]
