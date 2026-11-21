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
from tools import search_literature, search_manga

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
            "name": "search_manga",
            "description": (
                "Recherche/vérifie un manga sur MyAnimeList et renvoie démographie, genres, "
                "note et lien. Passe un titre précis ou un mot-clé lié à l'humeur."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Titre de manga ou mot-clé lié à l'humeur"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_literature",
            "description": (
                "Secondaire : recherche un LIVRE (roman) correspondant à une humeur, via "
                "OpenLibrary. À n'utiliser que pour une suggestion livre optionnelle en fin de réponse."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "mood_keyword": {"type": "string", "description": "Mot-clé représentant l'humeur"}
                },
                "required": ["mood_keyword"],
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


_JUSTIFICATION_CUES = (
    "parce que", "car ", "puisque", "pourquoi", "idéal", "parfait",
    "convient", "correspond", "reflète", "évoque", "résonne",
)


def evaluate_response(response: str) -> float:
    """Heuristic quality score (0..1) for monitoring.

    Rewards: a reading/reference link, an explicit justification, and a
    substantive (non-truncated) answer.
    """
    score = 0.0
    lowered = response.lower()
    if "http" in response:
        score += 0.4
    if any(cue in lowered for cue in _JUSTIFICATION_CUES):
        score += 0.3
    if len(response) >= 120:
        score += 0.3
    return round(min(score, 1.0), 2)


def _run_tool(name: str, args: dict, mood: str) -> str:
    if name == "search_manga":
        return search_manga(args.get("query", mood))
    if name == "search_literature":
        return search_literature(args.get("mood_keyword", mood))
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
                "Tu es un Bibliothécaire de l'Humeur spécialisé dans le MANGA, chaleureux et cultivé. "
                "L'utilisateur décrit son humeur ; tu recommandes 1 à 2 mangas qui lui correspondent, et POURQUOI.\n"
                "Mission : montrer que le manga n'est pas réservé aux enfants. Mais la PERTINENCE par rapport "
                "à l'humeur prime toujours : shōnen comme seinen sont les bienvenus (un shōnen comme Naruto "
                "peut parfaitement convenir).\n"
                "Méthode (sois efficace) :\n"
                "1. Pense à des mangas dont le TON et les THÈMES collent à l'humeur décrite.\n"
                "2. Fais UN SEUL appel à 'search_manga' (un mot-clé ou un titre) : il renvoie plusieurs "
                "candidats. Choisis-y 1 ou 2 œuvres bien notées et connues ; écarte celles qui ont très peu "
                "de votes. N'appelle PAS l'outil une fois par titre.\n"
                "3. Pour CHAQUE manga retenu (1 ou 2), écris en français, en Markdown, ainsi :\n"
                "**<Titre>** — <Auteur> · <Démographie> · ⭐ <note>/10\n"
                "- Pourquoi toi, maintenant : 1 à 2 phrases COURTES reliant le manga à l'humeur décrite.\n"
                "- Le moment à guetter : 1 à 2 phrases sur UN moment, arc ou scène PRÉCIS, et l'émotion qu'il "
                "procure (jamais un simple résumé de l'intrigue).\n"
                "- 📖 Fiche : <lien> — OBLIGATOIRE pour chaque manga. Copie EXACTEMENT le lien renvoyé par "
                "l'outil ; ne modifie jamais l'URL et ne l'omets JAMAIS.\n"
                "Chaque manga retenu DOIT se terminer par sa ligne « 📖 Fiche : » avec le lien exact. "
                "Reste concret, bienveillant et CONCIS. Ne donne jamais seulement un synopsis. "
                "Tu peux terminer par UNE courte ligne optionnelle suggérant un livre (via 'search_literature')."
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
            # Loop exhausted: force a final recommendation with no further tools,
            # so a flaky/slow search never costs the user an answer.
            nudge = {
                "role": "user",
                "content": (
                    "Conclus maintenant : recommande une œuvre adaptée à mon humeur en "
                    "justifiant ton choix, en incluant le lien de lecture uniquement s'il "
                    "est déjà disponible. N'appelle plus aucun outil."
                ),
            }
            try:
                final_resp = client.chat.completions.create(
                    model=settings.groq_model,
                    messages=messages + [nudge],
                )
                if final_resp.usage:
                    total_tokens += final_resp.usage.total_tokens
                final_content = final_resp.choices[0].message.content or ""
            except Exception:
                logger.exception("final-answer call failed")
                final_content = ""
            if not final_content:
                final_content = (
                    "Désolé, je n'ai pas réussi à finaliser une recommandation. Veuillez réessayer."
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
