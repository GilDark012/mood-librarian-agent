"""Core ReAct agent: safety guardrails, tool-calling loop, and monitoring.

The agent recommends a literary work based on the user's mood. It never
persists the user's input (mood text can reveal sensitive mental-health
information); only non-identifying metrics are logged.
"""
import json
import logging
import re
import time
import unicodedata

from openai import OpenAI

from config import settings
from tools import search_literature, search_web_links

logger = logging.getLogger(__name__)

# AI-transparency notice attached to every recommendation.
DISCLAIMER = (
    "Recommandation générée par une IA. Elle peut contenir des erreurs et ne "
    "constitue pas un avis médical, psychologique ou professionnel."
)

# Supportive message with concrete crisis resources, returned when the safety
# guardrail triggers. Keep real, actionable hotlines here.
CRISIS_MESSAGE = (
    "Il semble que vous traversiez une période très difficile, et je ne suis "
    "pas en mesure de vous aider sur ce sujet. Vous n'êtes pas seul·e et de "
    "l'aide existe :\n"
    "• France — 3114 (Numéro national de prévention du suicide), gratuit, 24h/24, 7j/7.\n"
    "• Urgences : 15 (SAMU) ou 112 (numéro d'urgence européen).\n"
    "Si vous êtes hors de France, contactez un service d'urgence local ou une "
    "ligne d'écoute de votre pays. Prenez soin de vous."
)

# Normalised (accent-free, lower-case) sensitive terms. Phrases match as
# substrings; single words match on word boundaries to avoid false positives
# on common words. NOTE: this is a keyword heuristic, not a clinical classifier;
# a model-assisted check is the recommended next step.
_SENSITIVE_WORDS = {
    "suicide",
    "suicider",
    "suicidaire",
    "suicidaires",
    "automutilation",
    "automutiler",
    "scarification",
}
_SENSITIVE_PHRASES = (
    "me tuer",
    "te tuer",
    "se tuer",
    "en finir",
    "mettre fin a mes jours",
    "mettre fin a ses jours",
    "envie de mourir",
    "veux mourir",
    "veux disparaitre",
    "me mutiler",
    "se mutiler",
    "self harm",
    "self-harm",
    "idees noires",
    "pensees noires",
    "pensees suicidaires",
    "crise suicidaire",
)

# Tools exposed to the LLM.
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search_literature",
            "description": "Recherche des œuvres littéraires correspondant à une humeur ou émotion.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mood_keyword": {"type": "string", "description": "Mot-clé représentant l'humeur"}
                },
                "required": ["mood_keyword"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_web_links",
            "description": "Recherche des liens web pour lire une œuvre spécifique.",
            "parameters": {
                "type": "object",
                "properties": {
                    "work_title": {"type": "string", "description": "Titre exact de l'œuvre à chercher"}
                },
                "required": ["work_title"],
            },
        },
    },
]

# Single client instance. A placeholder key keeps construction from failing in
# test/dev; real runs are validated at startup (see main.py).
client = OpenAI(
    api_key=settings.groq_api_key or "missing-api-key",
    base_url=settings.groq_base_url,
    timeout=settings.request_timeout,
    max_retries=1,
)


def _normalize(text: str) -> str:
    """Lower-case and strip accents so matching is accent-insensitive."""
    text = unicodedata.normalize("NFKD", text.casefold())
    return "".join(c for c in text if not unicodedata.combining(c))


def safety_check(user_input: str) -> bool:
    """Return True if the input looks like a self-harm / crisis situation."""
    norm = _normalize(user_input)
    if any(phrase in norm for phrase in _SENSITIVE_PHRASES):
        return True
    tokens = set(re.findall(r"\w+", norm))
    return bool(_SENSITIVE_WORDS & tokens)


def evaluate_response(response: str) -> float:
    """Basic quality heuristic (0..1): rewards a link and a justification."""
    score = 0.0
    if "http" in response:
        score += 0.5
    lowered = response.lower()
    if "parce que" in lowered or "car" in lowered:
        score += 0.5
    return score


def _run_tool(name: str, args: dict, mood: str) -> str:
    if name == "search_literature":
        return search_literature(args.get("mood_keyword", mood))
    if name == "search_web_links":
        return search_web_links(args.get("work_title", ""))
    return "Outil inconnu."


def agent_handler(mood: str) -> dict:
    """Main agent entry point. Returns a status dict (never raises)."""
    t0 = time.time()

    # 1. Safety guardrail — short-circuits before any LLM call.
    if safety_check(mood):
        return {
            "status": "blocked",
            "message": CRISIS_MESSAGE,
            "latency_s": round(time.time() - t0, 3),
        }

    # 2. System prompt enforcing the search -> link -> justify sequence.
    messages = [
        {
            "role": "system",
            "content": (
                "Tu es un Bibliothécaire de l'Humeur. L'utilisateur décrit son état d'esprit. "
                "Tu DOIS procéder ainsi : "
                "1. Utilise 'search_literature' pour trouver une œuvre adaptée à l'humeur. "
                "2. ENSUITE, utilise OBLIGATOIREMENT 'search_web_links' avec le titre de l'œuvre trouvée pour obtenir un lien de lecture. "
                "3. Enfin, rédige ta recommandation en justifiant ton choix et en incluant le lien."
            ),
        },
        {"role": "user", "content": mood},
    ]

    try:
        final_content = ""
        total_tokens = 0
        response_message = None

        for _ in range(settings.max_agent_steps):
            response = client.chat.completions.create(
                model=settings.groq_model,
                messages=messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
            )
            response_message = response.choices[0].message
            if response.usage:
                total_tokens += response.usage.total_tokens
            messages.append(response_message)

            # No more tool calls -> we have the final answer.
            if not response_message.tool_calls:
                final_content = response_message.content or ""
                break

            for tool_call in response_message.tool_calls:
                try:
                    args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    args = {}
                result = _run_tool(tool_call.function.name, args, mood)
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_call.function.name,
                    "content": result,
                })
        else:
            # Loop exhausted without a tool-free final answer.
            final_content = "Voici ce que j'ai trouvé : " + (
                (response_message.content if response_message else None) or "Recherche interrompue."
            )

        eval_score = evaluate_response(final_content)
        latency = round(time.time() - t0, 3)
        logger.info(
            "recommend ok: latency=%ss tokens=%s eval=%s",
            latency, total_tokens, eval_score,
        )

        return {
            "status": "success",
            "recommendation": final_content,
            "disclaimer": DISCLAIMER,
            "metrics": {
                "latency_s": latency,
                "total_tokens": total_tokens,
                "eval_quality_score": eval_score,
            },
        }

    except Exception:
        # Log full detail server-side; never leak internals to the caller.
        logger.exception("agent_handler failed")
        return {
            "status": "error",
            "message": "Une erreur interne est survenue. Veuillez réessayer plus tard.",
        }
