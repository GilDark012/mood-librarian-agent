# Mood Librarian Agent — Bibliothécaire de l'Humeur

[![CI](https://github.com/GilDark012/mood-librarian-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/GilDark012/mood-librarian-agent/actions/workflows/ci.yml)
[![Live](https://img.shields.io/badge/live-mood--librarian.onrender.com-4f46e5)](https://mood-librarian.onrender.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An agentic AI that recommends **manga** based on the user's mood — and explains
*why*, pointing to a specific moment worth reading for. The guiding idea: manga
aren't only for children. The user describes how they feel, and the agent picks
one or two fitting titles (shōnen or seinen), justifies each against the mood,
and links to them. Books are offered as an optional secondary suggestion. Built
as a FastAPI service with a ReAct-style tool-calling loop on a Groq-hosted LLM.

> ⚠️ Recommendations are AI-generated and are **not** medical or psychological
> advice. See [DISCLAIMER.md](DISCLAIMER.md) and [PRIVACY.md](PRIVACY.md).

## Features

- **ReAct agent loop** — the LLM reasons and calls tools iteratively (`agent.py`).
- **Tools** (`tools.py`):
  - `search_manga` — finds/verifies manga via MyAnimeList (Jikan): demographic, genres, rating, link.
  - `search_literature` — secondary: finds books via the OpenLibrary API.
  - `search_reading_link` — free book read/borrow links via OpenLibrary + Internet Archive (books phase).
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

Open http://localhost:8000/ for the web UI (interactive API docs at `/docs`).

## Configuration

All settings are read from environment variables / `.env` (see `.env.example`):

| Variable          | Required | Default                     | Description                                           |
|-------------------|----------|-----------------------------|-------------------------------------------------------|
| `GROQ_API_KEY`    | yes      | —                           | Groq LLM API key.                                     |
| `GROQ_MODEL`      | no       | `openai/gpt-oss-120b`       | Model id.                                             |
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
| GET    | `/`          | Web UI (the Swagger docs stay at `/docs`).               |
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
docker run -p 8000:8000 -e PORT=8000 --env-file .env mood-librarian
```

The container runs as a non-root user and binds `$PORT` (default `7860`).

## Deploy (Render, free tier)

The repo includes a [`render.yaml`](render.yaml) blueprint.

1. Push the repo to GitHub (already done).
2. On [render.com](https://render.com), **New → Blueprint**, connect this repo.
   Render reads `render.yaml` and provisions a free Docker web service.
3. Set the `GROQ_API_KEY` environment variable in the Render dashboard.
4. Deploy. Your app is served at `https://<service>.onrender.com`.

**Keep it warm:** the free tier sleeps after ~15 min of inactivity (cold start
~30–60 s). Add a free uptime monitor (e.g. UptimeRobot) that pings
`https://<service>.onrender.com/health` every ~10 minutes.

## Branching & deployment

- **`main`** is the **production** branch — it is exactly what's deployed at
  <https://mood-librarian.onrender.com>. Render auto-deploys every push to `main`.
- **`dev`** and short-lived **feature branches** hold work in progress.
- Flow: branch off `dev` → open a **pull request** into `main` → CI (ruff + pytest)
  runs → merge once green → Render deploys automatically.
- `main` is protected: a pull request with passing CI is required before changes
  reach production.

## License & author

Created and maintained by **Gil Allen Mounzeo** ([@GilDark012](https://github.com/GilDark012)).

Licensed under the **MIT License** — you may reuse the code with attribution.
See [LICENSE](LICENSE). © 2026 Gil Allen Mounzeo.

## Project structure

```
.
├── config.py            # Typed settings (.env)
├── agent.py             # ReAct loop, safety guardrail, monitoring
├── tools.py             # search_literature, search_reading_link
├── main.py              # FastAPI app (auth, CORS, rate limit, validation)
├── static/index.html    # Web UI served at /
├── requirements.txt     # Runtime dependencies
├── requirements-dev.txt # Test/lint dependencies
├── Dockerfile           # Container build (non-root, $PORT)
├── render.yaml          # Render deployment blueprint
├── tests/               # pytest suite
├── PRIVACY.md           # Privacy notice (GDPR)
├── DISCLAIMER.md        # AI + crisis disclaimer
└── .env.example         # Template for configuration
```
