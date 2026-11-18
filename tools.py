"""External tools the agent can call.

- search_literature: find works matching a mood (OpenLibrary).
- search_reading_link: find a free online reading/borrowing link for a work
  (OpenLibrary + Internet Archive).

Both use the reliable OpenLibrary JSON API (not web scraping) so they behave
consistently in production.
"""
import logging

import requests

logger = logging.getLogger(__name__)

OPENLIBRARY_URL = "https://openlibrary.org/search.json"
HTTP_TIMEOUT = 6


def search_literature(mood_keyword: str) -> str:
    """Search OpenLibrary for works matching a mood keyword.

    Returns up to 3 candidates with author, year, and an OpenLibrary link.
    """
    try:
        res = requests.get(
            OPENLIBRARY_URL,
            params={
                "q": mood_keyword,
                "limit": 3,
                "fields": "title,author_name,first_publish_year,key",
            },
            timeout=HTTP_TIMEOUT,
        )
        res.raise_for_status()
        docs = res.json().get("docs", [])

        results = []
        for d in docs:
            title = d.get("title", "Titre inconnu")
            author = ", ".join(d.get("author_name", ["Auteur inconnu"]))
            parts = [f"Titre: {title}", f"Auteur: {author}"]
            year = d.get("first_publish_year")
            if year:
                parts.append(f"Année: {year}")
            key = d.get("key", "")  # e.g. "/works/OL45883W"
            if key:
                parts.append(f"Fiche: https://openlibrary.org{key}")
            results.append(" | ".join(parts))

        return " || ".join(results) if results else "Aucun résultat trouvé pour cette humeur."
    except Exception as e:
        logger.warning("search_literature failed: %s", e)
        return "Erreur lors de la recherche littéraire."


def search_reading_link(work_title: str) -> str:
    """Find a free online reading/borrowing link for a work.

    Uses OpenLibrary's e-book access data: public-domain works link to the
    full text on the Internet Archive, borrowable ones to their lending page.
    Otherwise returns the OpenLibrary reference page so the agent can still
    point the reader somewhere.
    """
    try:
        res = requests.get(
            OPENLIBRARY_URL,
            params={
                "q": work_title,
                "limit": 1,
                "fields": "title,key,ia,ebook_access",
            },
            timeout=HTTP_TIMEOUT,
        )
        res.raise_for_status()
        docs = res.json().get("docs", [])
        if not docs:
            return "Aucune œuvre correspondante trouvée."

        doc = docs[0]
        key = doc.get("key", "")
        ol_page = f"https://openlibrary.org{key}" if key else "https://openlibrary.org"
        access = doc.get("ebook_access", "no_ebook")
        ia_ids = doc.get("ia") or []

        if access in ("public", "borrowable") and ia_ids:
            read_url = f"https://archive.org/details/{ia_ids[0]}"
            label = "Lecture gratuite" if access == "public" else "Emprunt gratuit"
            return f"{label} : {read_url} (fiche : {ol_page})"
        return f"Pas de version en ligne gratuite. Fiche de l'œuvre : {ol_page}"
    except Exception as e:
        logger.warning("search_reading_link failed: %s", e)
        return "Lien de lecture indisponible pour le moment."
