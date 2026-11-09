import requests
from duckduckgo_search import DDGS

def search_literature(mood_keyword: str) -> str:
    """Recherche des œuvres littéraires pertinentes (livres, mangas) selon l'humeur."""
    try:
        # Utilisation de l'API publique OpenLibrary
        res = requests.get(f"https://openlibrary.org/search.json?q={mood_keyword}&limit=3", timeout=5)
        res.raise_for_status()
        docs = res.json().get("docs", [])
        
        results = []
        for d in docs:
            title = d.get('title', 'Titre inconnu')
            author = ", ".join(d.get('author_name', ['Auteur inconnu']))
            results.append(f"Titre: {title} (Auteur: {author})")
            
        return " | ".join(results) if results else "Aucun résultat trouvé pour cette humeur."
    except Exception as e:
        return f"Erreur lors de la recherche littéraire: {str(e)}"

def search_web_links(work_title: str) -> str:
    """Recherche des liens pour lire l'œuvre en ligne (Web Search)."""
    try:
        # Recherche web gratuite via DuckDuckGo
        results = DDGS().text(f"lire en ligne {work_title}", max_results=2)
        links = [f"{r['title']} - {r['href']}" for r in results]
        return " | ".join(links) if links else "Aucun lien trouvé."
    except Exception as e:
        return f"Erreur lors de la recherche web: {str(e)}"