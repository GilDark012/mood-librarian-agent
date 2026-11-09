---
title: Mood Librarian
emoji: 📚
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# Mood Librarian Agent — Bibliothécaire de l'Humeur

An agentic AI that recommends literary works based on the user's mood. The user
describes their state of mind, and the agent finds a matching book and a link to
read it, justifying its choice. Built as a FastAPI service with a ReAct-style
tool-calling loop on top of a Groq-hosted LLM.

> ⚠️ Recommendations are AI-generated and are **not** medical or psychological
> advice. See [DISCLAIMER.md](DISCLAIMER.md) and [PRIVACY.md](PRIVACY.md).

## Features

- **ReAct agent loop** — the LLM reasons and calls tools iteratively (`agent.py`).
- **Tools** (`tools.py`):
  - `search_literature` — finds works via the OpenLibrary API.
  - `search_web_links` — finds reading links via DuckDuckGo search.
- **Safety guardrail** — accent-insensitive detection of self-harm / crisis
  language, returning concrete crisis resources instead of a recommendation.
- **Hardened API** — optional API-key auth, per-IP rate limiting, CORS control,
  input-length limits, request timeouts, and safe error responses.
- **Monitoring** — latency, token usage, and a basic quality score per request.
- **Privacy by default** — mood text is never persisted; logs contain metrics only.

## Getting started

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure
cp .env.example .env   # then edit .env and add your GROQ_API_KEY

# 3. Run the API
uvicorn main:app --reload
```

Open http://localhost:8000/ for the interactive Swagger docs.

## Configuration

All settings are read from environment variables / `.env` (see `.env.example`):

| Variable          | Required | Default                     | Description                                           |
|-------------------|----------|-----------------------------|-------------------------------------------------------|
| `GROQ_API_KEY`    | yes      | —                           | Groq LLM API key.                                     |
| `GROQ_MODEL`      | no       | `llama-3.3-70b-versatile`   | Model id.                                             |
| `GROQ_BASE_URL`   | no       | Groq OpenAI-compatible URL  | LLM endpoint.                                         |
| `API_KEY`         | no       | _(empty = open)_            | If set, callers must send it in the `X-API-Key` header. |
| `ALLOWED_ORIGINS` | no       | `*`                         | Comma-separated CORS origins.                         |
| `RATE_LIMIT`      | no       | `10/minute`                 | Per-IP limit on `/recommend`.                         |
| `MAX_MOOD_LENGTH` | no       | `500`                       | Max characters accepted for `mood`.                   |
| `REQUEST_TIMEOUT` | no       | `30`                        | LLM request timeout (seconds).                        |
| `MAX_AGENT_STEPS` | no       | `5`                         | Max ReAct iterations.                                 |

> **Before exposing the API online, set a strong `API_KEY`** (otherwise
> `/recommend` is public and spends your Groq quota) and restrict
> `ALLOWED_ORIGINS` to your frontend.

## API

| Method | Endpoint     | Description                                              |
|--------|--------------|----------------------------------------------------------|
| GET    | `/`          | Redirects to the Swagger UI (`/docs`).                   |
| GET    | `/health`    | Health check.                                            |
| POST   | `/recommend` | Body `{ "mood": "..." }` → recommendation. Needs `X-API-Key` if configured. |

Example:

```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{"mood": "je me sens nostalgique"}'
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

CI runs linting and tests on every push/PR (`.github/workflows/ci.yml`).

## Docker

```bash
docker build -t mood-librarian .
docker run -p 7860:7860 --env-file .env mood-librarian
```

The container runs as a non-root user and listens on `$PORT` (default `7860`,
suitable for Hugging Face Spaces with SDK=docker).

## Project structure

```
.
├── config.py            # Typed settings (.env)
├── agent.py             # ReAct loop, safety guardrail, monitoring
├── tools.py             # search_literature, search_web_links
├── main.py              # FastAPI app (auth, CORS, rate limit, validation)
├── requirements.txt     # Runtime dependencies
├── requirements-dev.txt # Test/lint dependencies
├── Dockerfile           # Container build (non-root, $PORT)
├── tests/               # pytest suite
├── PRIVACY.md           # Privacy notice (GDPR)
├── DISCLAIMER.md        # AI + crisis disclaimer
└── .env.example         # Template for configuration
```
