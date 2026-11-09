import os
import json
import time
from openai import OpenAI
from tools import search_literature, search_web_links

# Initialisation du client (Nécessite la variable d'environnement OPENAI_API_KEY)
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Guardrails : Liste de mots-clés sensibles nécessitant un rejet de la requête
SENSITIVE_KEYWORDS = ["suicide", "se suicider", "mettre fin à ses jours", "en finir", "en finir avec la vie", "je veux mourir", "mourir", "mort", "décès", "tuer", "se tuer", "me tuer", "te tuer", "le tuer", "la tuer", "homicide", "meurtre", "assassiner", "dépression", "dépressif", "idées noires", "désespoir", "désespéré", "automutilation", "automutiler", "se mutiler", "scarification", "self-harm", "self harm", "autodestruction", "je veux disparaître", "je n’en peux plus", "je veux en finir", "envie de mourir", "pensées suicidaires", "crise suicidaire"]

# Outils déclarés pour le LLM
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
                "required": ["mood_keyword"]
            }
        }
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
                "required": ["work_title"]
            }
        }
    }
]

def safety_check(user_input: str) -> bool:
    """Vérifie si la requête contient des propos sensibles."""
    user_input_lower = user_input.lower()
    return any(word in user_input_lower for word in SENSITIVE_KEYWORDS)

def evaluate_response(response: str) -> float:
    """Eval basique : vérifie si l'agent a inclus une justification et des liens (score de 0 à 1)."""
    score = 0.0
    if "http" in response: score += 0.5
    if "parce que" in response.lower() or "car" in response.lower(): score += 0.5
    return score

def agent_handler(mood: str) -> dict:
    """Handler principal de l'agent."""
    t0 = time.time()
    
    # 1. Safety Guardrail
    if safety_check(mood):
        return {
            "status": "blocked",
            "message": "Il semble que vous traversiez une période difficile. N'hésitez pas à contacter un professionnel de santé ou une ligne d'écoute. Prenez soin de vous.",
            "latency_s": round(time.time() - t0, 3)
        }

    # 2. Le System Prompt amélioré pour forcer l'enchaînement
    messages = [
        {
            "role": "system", 
            "content": (
                "Tu es un Bibliothécaire de l'Humeur. L'utilisateur décrit son état d'esprit. "
                "Tu DOIS procéder ainsi : "
                "1. Utilise 'search_literature' pour trouver une œuvre adaptée à l'humeur. "
                "2. ENSUITE, utilise OBLIGATOIREMENT 'search_web_links' avec le titre de l'œuvre trouvée pour obtenir un lien de lecture. "
                "3. Enfin, rédige ta recommandation en justifiant ton choix et en incluant le lien."
            )
        },
        {"role": "user", "content": mood}
    ]

    try:
        # 3. La vraie boucle ReAct (Reason + Act)
        max_steps = 5
        current_step = 0
        final_content = ""
        total_tokens = 0
        
        while current_step < max_steps:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile", # Ou "gpt-4o-mini" selon ce que vous avez choisi
                messages=messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            total_tokens += response.usage.total_tokens
            messages.append(response_message)
            
            # Si le LLM ne veut plus appeler d'outil, on a notre réponse finale !
            if not response_message.tool_calls:
                final_content = response_message.content
                break
                
            # S'il veut appeler des outils, on les exécute
            for tool_call in response_message.tool_calls:
                args = json.loads(tool_call.function.arguments)
                
                if tool_call.function.name == "search_literature":
                    result = search_literature(args.get("mood_keyword", mood))
                elif tool_call.function.name == "search_web_links":
                    result = search_web_links(args.get("work_title", ""))
                else:
                    result = "Outil inconnu."
                
                # On ajoute le résultat de l'outil dans l'historique pour le prochain tour
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_call.function.name,
                    "content": result
                })
            
            current_step += 1
            
        # Sécurité au cas où l'agent boucle à l'infini
        if current_step >= max_steps:
            final_content = "Voici ce que j'ai trouvé : " + (response_message.content or "Recherche interrompue.")

        # 4. Monitoring (Coût et Eval)
        cost_usd = (total_tokens / 1_000_000) * 0.30 
        eval_score = evaluate_response(final_content)

        return {
            "status": "success",
            "recommendation": final_content,
            "metrics": {
                "latency_s": round(time.time() - t0, 3),
                "total_tokens": total_tokens,
                "estimated_cost_usd": round(cost_usd, 6),
                "eval_quality_score": eval_score
            }
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}