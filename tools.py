"""External tools the agent can call: literary search and web link search."""
import logging

import requests
from ddgs import DDGS

logger = logging.getLogger(__name__)

OPENLIBRARY_URL = "https://openlibrary.org/search.json"
HTTP_TIMEOUT = 5


def search_literature(mood_keyword: str) -> str:
    """Search OpenLibrary for literary works matching a mood keyword."""
    try:
        # `params=` handles URL-encoding of the keyword (spaces, &, #, ...).
        res = requests.get(
            OPENLIBRARY_URL,
            params={"q": mood_keyword, "limit": 3},
            timeout=HTTP_TIMEOUT,
        )
        res.raise_for_status()
        docs = res.json().get("docs", [])

        results = []
        for d in docs:
            title = d.get("title", "Titre inconnu")
            author = ", ".join(d.get("author_name", ["Auteur inconnu"]))
            results.append(f"Titre: {title} (Auteur: {author})")

        return " | ".join(results) if results else "Aucun résultat trouvé pour cette humeur."
    except Exception as e:
        logger.warning("search_literature failed: %s", e)
        return "Erreur lors de la recherche littéraire."


def search_web_links(work_title: str) -> str:
    """Search the web (DuckDuckGo) for links to read a given work online."""
    try:
        results = DDGS().text(f"lire en ligne {work_title}", max_results=2)
        links = [f"{r['title']} - {r['href']}" for r in results]
        return " | ".join(links) if links else "Aucun lien trouvé."
    except Exception as e:
        logger.warning("search_web_links failed: %s", e)
        return "Erreur lors de la recherche web."
