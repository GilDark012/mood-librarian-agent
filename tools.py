"""External tools the agent can call.

- search_manga: find/verify manga and get demographic, rating and link
  (MyAnimeList via the Jikan API). The primary tool.
- search_literature: find books matching a mood (OpenLibrary) — secondary.
- search_reading_link: free online reading/borrowing link for a book
  (OpenLibrary + Internet Archive) — kept for the later books phase.

All use reliable JSON APIs (not web scraping) so they behave consistently
in production.
"""
import logging
import time

import requests

logger = logging.getLogger(__name__)

OPENLIBRARY_URL = "https://openlibrary.org/search.json"
JIKAN_URL = "https://api.jikan.moe/v4/manga"
HTTP_TIMEOUT = 6
JIKAN_RETRY_WAIT = 0.6  # Jikan rate-limits aggressively; back off and retry once.


def search_manga(query: str) -> str:
    """Search MyAnimeList (via Jikan) for manga and return rich candidates.

    `query` is a title or keyword. Returns up to 4 candidates ordered by
    popularity (a rough quality gate), each with author, demographic
    (shounen/seinen/...), genres, MAL score + vote count, link and a short
    synopsis — enough for the agent to pick on mood-fit and justify the choice.
    """
    data = None
    for attempt in range(2):
        try:
            res = requests.get(
                JIKAN_URL,
                params={"q": query, "limit": 6, "sfw": "true"},
                timeout=HTTP_TIMEOUT,
            )
            res.raise_for_status()
            data = res.json().get("data", [])
            break
        except Exception as e:
            logger.warning("search_manga attempt %s failed: %s", attempt + 1, e)
            if attempt == 0:
                time.sleep(JIKAN_RETRY_WAIT)

    if data is None:
        return "Recherche manga indisponible pour le moment."
    if not data:
        return "Aucun manga correspondant trouvé."

    try:
        # Prefer well-known titles (more members ~ more reliable + less obscure).
        data.sort(key=lambda m: (m.get("members") or 0), reverse=True)

        out = []
        for m in data[:4]:
            title = m.get("title") or "Titre inconnu"
            authors = ", ".join(a.get("name", "") for a in m.get("authors", [])) or "Auteur inconnu"
            demo = ", ".join(d.get("name", "") for d in m.get("demographics", [])) or "Non précisé"
            tags = [g.get("name", "") for g in (m.get("genres", []) + m.get("themes", []))]
            genres = ", ".join(t for t in tags if t)[:120]
            score = m.get("score")
            scored_by = m.get("scored_by")
            url = m.get("url", "")
            syn = " ".join((m.get("synopsis") or "").split())
            if len(syn) > 220:
                syn = syn[:220] + "…"

            parts = [f"Titre: {title}", f"Auteur: {authors}", f"Démographie: {demo}"]
            if genres:
                parts.append(f"Genres/thèmes: {genres}")
            if score:
                parts.append(f"Note MAL: {score}/10 ({scored_by} votes)")
            if url:
                parts.append(f"Fiche: {url}")
            if syn:
                parts.append(f"Résumé: {syn}")
            out.append(" | ".join(parts))

        return " || ".join(out)
    except Exception as e:
        logger.warning("search_manga failed: %s", e)
        return "Recherche manga indisponible pour le moment."


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
