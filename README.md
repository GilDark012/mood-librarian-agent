# Mood Librarian Agent — Bibliothécaire de l'Humeur

An agentic AI that recommends literary works based on the user's mood. The user
describes their state of mind, and the agent finds a matching book and a link to
read it, justifying its choice. Built as a FastAPI service with a ReAct-style
tool-calling loop on top of a Groq-hosted LLM.

## Features

- **ReAct agent loop** — the LLM reasons and calls tools iteratively (`agent.py`).
- **Tools** (`tools.py`):
  - `search_literature` — finds works via the OpenLibrary API.
  - `search_web_links` — finds reading links via DuckDuckGo search.
- **Safety guardrails** — blocks sensitive/at-risk requests and returns a support message.
- **Monitoring** — latency, token usage, estimated cost, and a basic quality eval score.
- **FastAPI API** (`main.py`) with `/recommend`, `/health`, and Swagger UI at `/`.

## Getting started

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure your API key
cp .env.example .env   # then edit .env and add your GROQ_API_KEY

# 3. Run the API
uvicorn main:app --reload
```

Open http://localhost:8000/ for the interactive Swagger docs.

## API

| Method | Endpoint     | Description                                 |
|--------|--------------|---------------------------------------------|
| GET    | `/`          | Redirects to the Swagger UI (`/docs`).      |
| GET    | `/health`    | Health check.                               |
| POST   | `/recommend` | Body `{ "mood": "..." }` → recommendation.  |

## Docker

```bash
docker build -t mood-librarian -f Dockerfile .
docker run -p 7860:7860 --env-file .env mood-librarian
```

The container listens on port `7860` (configured for Hugging Face Spaces).

## Environment variables

| Variable       | Description                         |
|----------------|-------------------------------------|
| `GROQ_API_KEY` | API key for the Groq LLM endpoint.  |

## Project structure

```
.
├── agent.py          # ReAct agent loop, guardrails, monitoring
├── tools.py          # search_literature, search_web_links
├── main.py           # FastAPI app
├── requirements.txt  # Python dependencies
├── Dockerfile        # Container build (port 7860)
└── .env.example      # Template for required env vars
```
