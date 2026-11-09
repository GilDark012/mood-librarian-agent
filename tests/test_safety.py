"""Unit tests for the safety guardrail."""
import pytest

from agent import safety_check


@pytest.mark.parametrize("text", [
    "je pense au suicide",
    "je veux mourir",
    "je veux en finir",
    "j'ai envie de mourir",
    "je me fais de l'automutilation",
    "pensees suicidaires",
    "I want to self-harm",
    "JE VEUX MOURIR",  # case-insensitive
])
def test_blocks_crisis_inputs(text):
    assert safety_check(text) is True


@pytest.mark.parametrize("text", [
    "je suis joyeux et plein d'énergie",
    "je me sens mort de fatigue",  # common idiom, not a crisis
    "un roman sur la mort d'un proche",  # literary theme
    "je cherche un livre mélancolique",
    "une ambiance calme et apaisante",
])
def test_allows_benign_inputs(text):
    assert safety_check(text) is False
