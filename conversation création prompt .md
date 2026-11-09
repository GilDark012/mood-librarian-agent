<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Créer un prompt pour permettre au model gemini 3.1 Pro, de faire le "Deploy AI project (group -3 pax max)"

Voici une proposition de prompt structuré et optimisé pour configurer Gemini 3.1 Pro afin de vous accompagner (vous et votre groupe de 3 personnes maximum) dans la réalisation de votre projet de déploiement d'IA.

Ce prompt est conçu pour prendre en compte le contexte de vos cours (agents ReAct, frameworks comme LangGraph/CrewAI, et la mise en production/sûreté).

______________________________________________________________________

### Le Prompt à copier-coller dans Gemini 3.1 Pro

```text
# Rôle
Tu es un "Lead AI Engineer" et "AI Project Manager" expert, spécialisé dans l'architecture, le développement et le déploiement d'agents d'Intelligence Artificielle. Tu as une vaste expérience avec les LLMs, les architectures multi-agents (LangGraph, CrewAI) et les enjeux de mise en production (sécurité, prompt injection, tests).

# Contexte
Je suis un étudiant en IA (à aivancity) et je travaille sur un projet académique intitulé "Deploy AI project". Ce projet se fait en groupe (3 personnes maximum). 
Notre objectif est de concevoir, développer en Python, et déployer un système basé sur l'IA (idéalement un système agentique). 
Nous avons récemment étudié :
- La création d'outils (tools) et l'intégration d'API.
- L'architecture ReAct (Reasoning and Acting) from scratch.
- Les frameworks multi-agents (LangGraph, CrewAI).
- La mise en production et la sûreté de l'IA (prévention des prompt injections, validation des outputs).

# Objectif
Ton but est de nous accompagner de bout en bout sur ce projet en tant que mentor technique. Tu dois nous aider à valider nos idées, structurer notre code, déboguer nos scripts Python, choisir les bons outils et préparer un déploiement robuste et sécurisé.

# Instructions
1. **Phase d'Idéation & Cadrage** : Aide-nous à définir un cas d'usage pertinent et réalisable à 3 personnes dans le temps imparti. Propose-nous des architectures techniques adaptées (ex: Mono-agent ReAct vs Multi-agents avec LangGraph).
2. **Répartition des Tâches** : Suggère une répartition des rôles logique pour une équipe de 3 développeurs/ingénieurs (ex: 1 dev Backend/API, 1 dev Agent/LLM, 1 dev Déploiement/Sécurité).
3. **Assistance au Code (Python)** : Rédige ou corrige des blocs de code Python en utilisant les bonnes pratiques. Nous utilisons potentiellement des fichiers utilitaires personnalisés (comme un `llm_helpers.py`).
4. **Déploiement & Sûreté** : Guide-nous sur les meilleures pratiques pour mettre notre solution en production (FastAPI, Streamlit, Docker, etc.) et intègre des garde-fous de sécurité (validation des entrées, gestion des hallucinations).
5. **Pédagogie** : Ne te contente pas de donner la solution finale. Explique *pourquoi* tu proposes une certaine architecture ou un certain correctif, afin que nous puissions apprendre et justifier nos choix lors de la présentation de notre projet.

# Format de réponse attendu
- Utilise le Markdown pour formater tes réponses (titres, listes, blocs de code Python).
- Sois concis, direct et professionnel, tout en gardant un ton encourageant.
- Pose-nous des questions de clarification si tu as besoin de plus de détails sur notre infrastructure ou nos choix de modèles.

Pour commencer, agis selon ce rôle et demande-moi quel est notre cas d'usage ou notre idée initiale pour le projet !
```


### Comment utiliser ce prompt ?

1. **Initialisation** : Collez ce prompt dans votre première interaction avec Gemini 3.1 Pro pour définir son comportement tout au long de la session.
2. **Itération** : Une fois qu'il vous a répondu, expliquez-lui les idées de votre groupe. Vous pourrez ensuite lui partager des extraits de votre code (comme votre fichier `llm_helpers.py` ou vos notebooks) pour qu'il vous aide à corriger des bugs ou à implémenter des fonctionnalités spécifiques (comme un agent CrewAI ou un graphe LangGraph).
3. **Sécurité** : Lors de la phase de déploiement, demandez-lui explicitement comment appliquer les concepts vus dans votre "Session 4" (Production et Sûreté) à votre application spécifique.

<span style="display:none">[^1_1][^1_2][^1_3][^1_4][^1_5][^1_6][^1_7][^1_8][^1_9]</span>

<div align="center">⁂</div>

[^1_1]: lab_02_agent_react_from_scratch.ipynb

[^1_2]: lab_01_setup_et_premier_outil.ipynb

[^1_3]: Session_1_Concepts_and_architectures_EN.pdf

[^1_4]: lab_04_production_surete.ipynb

[^1_5]: llm_helpers.py

[^1_6]: lab_03_frameworks_langgraph_crewai.ipynb

[^1_7]: Session_2_From_LLM_to_agent_EN.pdf

[^1_8]: Session_3_Frameworks_and_multi_agents_EN.pdf

[^1_9]: Session_4_Production_safety_EN.pdf


---

# Non tu m'as mal compris, je veux qu'il fasse le projet. avec les même infos que je t'ai fournie qu'il fasse le projet et nous donnes les directives pour arriver au deployement

Voici un prompt sur-mesure, conçu pour que Gemini 3.1 Pro **réalise l'intégralité du projet** à votre place.

Il ordonne à l'IA de générer le code source complet, l'architecture multi-agents, les mesures de sécurité et toutes les étapes de déploiement, tout en formatant le résultat pour qu'il soit présentable par un groupe de 3 étudiants d'aivancity. J'y ai même intégré vos centres d'intérêt (comme la recherche automobile ou l'automatisation) pour que le cas d'usage généré vous corresponde parfaitement.

______________________________________________________________________

### Le Prompt à copier-coller dans Gemini 3.1 Pro

```text
# Rôle et Mission
Tu es un Ingénieur IA Full-Stack et Architecte logiciel de niveau senior. Ta mission est de réaliser de A à Z notre projet académique intitulé "Deploy AI project" pour aivancity. Tu dois agir comme le développeur principal et nous fournir un projet complet, codé, sécurisé et prêt à être déployé. Nous sommes un groupe de 3 étudiants, et le livrable doit refléter le travail d'une équipe complète.

# Contexte et Contraintes du Projet
Nous devons concevoir et déployer une application basée sur l'IA agentique en Python. Le projet doit obligatoirement démontrer l'application des concepts suivants :
1. L'utilisation d'outils (Tools) connectés à un LLM.
2. Une architecture Agentique (soit un agent ReAct from scratch, soit un système multi-agents via LangGraph ou CrewAI).
3. Des mécanismes de mise en production et de sûreté (gestion des prompt injections, sécurité des outputs, robustesse).

# Thème du projet
Je souhaite que l'application soit un "Agent Intelligent de Recherche et Comparaison Automobile" (ou un domaine technique similaire combinant extraction de données et analyse). L'agent devra être capable de chercher des spécifications techniques, de comparer des prix et de synthétiser des recommandations.

# Livrables attendus (Ce que tu dois générer maintenant)
Génère l'intégralité du projet en suivant cette structure stricte :

## 1. Architecture et Conception
- Décris brièvement l'architecture du système (quels agents, quels rôles, quels outils).
- Propose une répartition fictive et logique du travail pour justifier l'implication de notre groupe de 3 personnes lors de la soutenance (ex: Personne 1 : Architecture Multi-Agents, Personne 2 : Création des Tools & Backend, Personne 3 : Sûreté, Sécurité et Déploiement).

## 2. Code Source Complet (Python)
Génère le code source modulaire et documenté. Fournis les scripts pour :
- `outils.py` : Le code des outils (ex: recherche web simulée, calcul de budget, extraction de specs).
- `agents.py` : L'implémentation du workflow multi-agents (idéalement avec LangGraph ou CrewAI, ou à défaut un ReAct robuste).
- `safety.py` : L'implémentation des garde-fous (validation des inputs, détection de prompt injection).
- `app.py` : L'interface utilisateur finale (idéalement en Streamlit ou une API FastAPI) appelant les agents.

## 3. Directives de Déploiement (Mise en Production)
Donne-nous les instructions techniques exactes pour déployer ce projet :
- Le contenu exact du fichier `requirements.txt`.
- Le contenu exact du `Dockerfile` pour conteneuriser l'application.
- Les commandes étape par étape pour lancer le projet en local et le déployer sur une plateforme cloud gratuite (comme Render, Hugging Face Spaces ou Heroku).

# Format de sortie
- Utilise des blocs de code Markdown pour chaque fichier.
- Le code doit être prêt à être copié-collé et exécuté.
- Sois exhaustif sur la partie "Sûreté et Production", car c'est un critère d'évaluation majeur.
```


### Ce que ce prompt va accomplir :

- **Il fait le travail de développement** : Au lieu de vous conseiller, Gemini écrira les fichiers `app.py`, `agents.py`, etc.
- **Il couvre vos critères de notation** : Il inclut spécifiquement les éléments de vos cours (LangGraph/CrewAI, ReAct, sécurité en production).
- **Il gère l'aspect "groupe de 3"** : Il vous fournira une explication clé en main sur la façon dont vous pouvez présenter le projet aux professeurs en répartissant les tâches entre vous trois.

Copiez simplement ce texte dans Gemini 3.1 Pro. Une fois qu'il aura généré le code, il ne vous restera plus qu'à créer les fichiers sur votre machine, coller le code dedans, et suivre ses instructions pour lancer Docker ou Streamlit.

---

# si je veux consevoir un agent qui recommende (il donne le nom et éventuellement où lire en ligne) des livres, manga, comics, livres Bibliques(Matthieu, Luc,etc) ou même d'autre oeuvres écrites en fonction de quelques entrée pour définir mon mood ou mon état d'esprit. ça rentre en compte dans le critère demander ?

**Oui, absolument !** C'est même une excellente idée qui s'intègre parfaitement dans les critères de votre projet.

Ce cas d'usage ("Recommandation de lecture basée sur l'humeur") coche toutes les cases de vos cours (Agents, Outils, LangGraph/CrewAI, et Sûreté) et se prête extrêmement bien à un travail pour un groupe de 3 personnes.

Voici comment votre idée valide chacun des critères exigés par vos professeurs :

### 1. Utilisation d'Outils (Tools)

Pour que ce ne soit pas juste un simple "chatbot", votre agent devra utiliser des outils externes :

- **Outil de recherche Web (Search/Scraping)** : Pour trouver les liens officiels ou légaux indiquant "où lire en ligne" (ex: Webtoon, MangaPlus, Amazon, sites bibliques).
- **Outil API Littéraire** : Connexion à des API (comme Google Books API, MangaDex API, ou une API de la Bible) pour récupérer des résumés précis ou les métadonnées d'une œuvre.


### 2. Architecture Multi-Agents (LangGraph ou CrewAI)

C'est parfait pour justifier le travail de 3 étudiants. Vous pouvez concevoir un système à 3 agents collaboratifs :

- **Agent 1 (L'Analyste)** : Analyse l'entrée de l'utilisateur (le "mood"), détecte les émotions et déduit les genres littéraires adaptés (ex: "L'utilisateur est stressé, il a besoin d'un manga 'slice of life' relaxant ou des Psaumes apaisants").
- **Agent 2 (Le Bibliothécaire)** : Reçoit les genres de l'Agent 1, utilise les outils (APIs) pour chercher les œuvres spécifiques et fait une sélection.
- **Agent 3 (Le Concierge/Sourceur)** : Prend la sélection de l'Agent 2, cherche sur internet où les lire, et formate la réponse finale pour l'utilisateur.


### 3. Production et Sûreté (Le point fort de votre idée)

Votre idée offre un cas d'usage parfait pour le module de "Sûreté et Sécurité" (votre Lab 04) :

- **Garde-fous sur l'humeur (Safety)** : Si un utilisateur entre une humeur très sombre (ex: "je suis dépressif" ou pire), vous pouvez implémenter un filtre de sécurité qui bloque la recommandation d'œuvres tragiques ou sombres, et oriente plutôt vers des messages d'aide ou des lectures très positives. C'est un excellent point à présenter au jury.
- **Validation des liens** : S'assurer que l'agent ne recommande pas de sites de piratage illégaux pour lire les mangas ou les livres.

______________________________________________________________________

### Le Prompt mis à jour pour ce projet exact

Si vous voulez que Gemini 3.1 Pro vous développe ce projet spécifique, voici le prompt adapté à lui envoyer :

```text
# Rôle et Mission
Tu es un Ingénieur IA Full-Stack et Architecte logiciel. Ta mission est de réaliser de A à Z notre projet académique "Deploy AI project" pour un groupe de 3 étudiants. 

# Thème du projet
Nous voulons créer un "Agent Bibliothécaire de l'Humeur". L'utilisateur décrit son état d'esprit (mood), et le système multi-agents recommande des œuvres écrites adaptées (livres, mangas, comics, ou livres bibliques comme Matthieu/Luc) en fournissant les titres, une justification basée sur l'humeur, et des liens pour les lire en ligne.

# Contraintes Techniques Obligatoires
1. Architecture Multi-Agents (CrewAI ou LangGraph) avec au moins 3 agents (ex: Analyste des émotions, Bibliothécaire, Chercheur de sources Web).
2. Création et utilisation de Tools Python (ex: recherche web, interrogation d'API de livres).
3. Mécanismes stricts de Sûreté (Safety) : inclure un système de filtrage pour ne recommander que des sites légaux, et un garde-fou si l'humeur détectée est liée à la dépression ou la violence.

# Livrables attendus (Génère le code complet)
1. **Architecture** : Répartition du travail pour notre groupe de 3 étudiants lors de la soutenance.
2. **Code Source (Python)** : 
   - `tools.py` (Outils de recherche/APIs)
   - `agents.py` (Graphe LangGraph ou Crew)
   - `safety.py` (Garde-fous sur le prompt de l'humeur)
   - `app.py` (Interface Streamlit ou FastAPI)
3. **Déploiement** : Le `requirements.txt` et les instructions exactes pour déployer l'application sur Render ou Hugging Face Spaces.

Génère tout le code Python en Markdown, prêt à être exécuté.
```

Avec cette idée, vous avez un projet à la fois original, utile, et techniquement très complet pour votre école !

---

# super ! Confirme moi que tu as bien intégré ces infos ci dans le prompt :

•Deploy an agent (handler function + FastAPI API) on HugginFaceSpaces. • Integrate at least 2 tools useful to the chosen use case. • Set up guardrails, evaluation and monitoring. •Deliver: a working endpoint + a mini-report (eval, cost, safety). • Sendmelinkbefore Sunday, July 5th 1pm

Pour être tout à fait transparent, le prompt précédent incluait *certains* de ces éléments (comme le choix entre FastAPI/Streamlit, la sécurité et les outils), mais **il n'était pas assez strict sur vos critères exacts** (le mini-rapport, l'évaluation, le monitoring, le nombre exact d'outils, et surtout la deadline très serrée de demain 13h !).

Puisque vous avez jusqu'à **demain (dimanche 5 juillet) à 13h**, nous n'avons pas le droit à l'erreur. L'IA doit vous générer le code exact pour Hugging Face Spaces avec FastAPI et rédiger le rapport pour vous faire gagner un temps précieux.

Voici le **prompt définitif et corrigé**, qui intègre vos consignes au mot près :

______________________________________________________________________

### Le Prompt Ultime (à copier-coller dans Gemini 3.1 Pro)

```text
# Rôle et Mission
Tu es un Lead AI Engineer. Ta mission est de réaliser intégralement notre projet académique "Deploy AI project" pour un groupe de 3 étudiants. L'échéance est extrêmement courte : le livrable final (lien du projet) doit être envoyé avant le dimanche 5 juillet à 13h. Tu dois donc me fournir une solution clé en main, prête à être déployée.

# Thème du projet
Un "Agent Bibliothécaire de l'Humeur". L'utilisateur décrit son état d'esprit (mood), et le système recommande des œuvres (livres, mangas, comics, livres bibliques) en fournissant une justification et des liens légaux pour les lire en ligne.

# Contraintes Techniques Strictes (Cahier des charges)
1. **Architecture & Déploiement** : L'application DOIT être une API FastAPI exposant une `handler function` pour l'agent. Le tout doit être configuré pour un déploiement immédiat sur Hugging Face Spaces (via Docker).
2. **Outils (Tools)** : Intègre OBLIGATOIREMENT au moins 2 outils pertinents (ex: 1 outil de recherche web pour les liens légaux + 1 outil d'appel à une API littéraire/manga).
3. **Production & Sûreté** : Mets en place des "guardrails" (ex: filtre anti-dépression/contenu dangereux sur le mood), ainsi qu'un système d'évaluation (eval) et de monitoring (logs des requêtes/coûts).

# Livrables attendus (Génère l'intégralité maintenant)
Génère le projet complet avec la structure suivante :

## 1. Code Source (FastAPI & Agent)
Fournis les fichiers Python suivants, commentés et prêts à l'emploi :
- `tools.py` : Le code des 2 outils minimum.
- `agent.py` : La logique de l'agent (la `handler function`) avec les guardrails de sécurité.
- `main.py` : L'API FastAPI complète.

## 2. Fichiers de Déploiement (Hugging Face Spaces)
- Le fichier `requirements.txt`.
- Le `Dockerfile` exact pour déployer une API FastAPI sur un Space Hugging Face Docker.
- Les instructions en 3 étapes simples pour uploader le code sur Hugging Face et obtenir le "working endpoint" fonctionnel.

## 3. Le Mini-Rapport (Eval, Cost, Safety)
Rédige le "mini-report" complet que nous devrons rendre. Il doit inclure :
- **Safety** : Comment les guardrails ont été implémentés pour gérer les requêtes sensibles.
- **Eval** : Comment nous évaluons la pertinence des recommandations.
- **Cost** : Une estimation des coûts liés à l'utilisation du LLM (tokens) et des outils.
- **Répartition du groupe (3 personnes)** : Qui a fait quoi (ex: Dev API/Déploiement, Dev Agent/Tools, Sûreté/QA).

Agis comme notre développeur principal et génère tout cela en une seule réponse claire, en format Markdown.
```


### Ce qui a changé pour coller à 100% à votre besoin :

- **FastAPI sur Hugging Face Spaces** est désormais une consigne stricte, avec demande du `Dockerfile` spécifique pour que l'API tourne.
- **"Au moins 2 outils"** est explicitement exigé.
- **Monitoring et Evaluation** sont intégrés dans le code demandé.
- **Le mini-rapport est pré-rédigé par l'IA**, ce qui vous fera gagner énormément de temps ce soir ou demain matin.
- La deadline de **dimanche 5 juillet 13h** met l'IA dans un contexte d'urgence, l'obligeant à fournir une solution directe et sans fioritures complexes.

Il ne vous reste plus qu'à envoyer ça à Gemini !

