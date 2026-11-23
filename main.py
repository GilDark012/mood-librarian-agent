"""FastAPI entry point for the Mood Librarian agent."""
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Request, Security
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, StringConstraints
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

import stats
from agent import DISCLAIMER, agent_handler, journey_handler
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not settings.groq_api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    if not settings.auth_enabled:
        logger.warning(
            "API_KEY is not set: /recommend is PUBLIC. Set API_KEY before exposing online."
        )
    yield


app = FastAPI(
    title="Agent Bibliothécaire de l'Humeur",
    description=(
        "Recommande une œuvre littéraire selon votre humeur.\n\n"
        f"⚠️ {DISCLAIMER}\n\n"
        "Les requêtes ne sont pas conservées. Voir PRIVACY.md et DISCLAIMER.md."
    ),
    version="1.0.0",
    lifespan=lifespan,
)
app.state.limiter = limiter

# CORS: restrict to configured origins. Credentials are disabled, so "*" is
# safe as a public default; set ALLOWED_ORIGINS to lock this down in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
def _rate_limit_handler(request: Request, exc: RateLimitExceeded):
    stats.record_rate_limited()
    return JSONResponse(status_code=429, content={"detail": "Trop de requêtes. Réessayez plus tard."})


# Baseline security headers on every response (clickjacking, sniffing, referrer).
_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data: https://fastapi.tiangolo.com; "
        "connect-src 'self'; frame-ancestors 'none'; base-uri 'self'"
    ),
}


@app.middleware("http")
async def _add_security_headers(request: Request, call_next):
    response = await call_next(request)
    for key, value in _SECURITY_HEADERS.items():
        response.headers.setdefault(key, value)
    return response


# --- Auth: require X-API-Key only when an API key is configured. ---
_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(key: str | None = Security(_api_key_header)) -> None:
    if settings.auth_enabled and key != settings.api_key:
        raise HTTPException(status_code=401, detail="Clé API invalide ou manquante.")


MoodStr = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=settings.max_mood_length),
]


class MoodRequest(BaseModel):
    mood: MoodStr


class JourneyRequest(BaseModel):
    current_mood: MoodStr
    desired_mood: Annotated[
        str, StringConstraints(strip_whitespace=True, max_length=settings.max_mood_length)
    ] = ""


_INDEX_HTML = Path(__file__).parent / "static" / "index.html"


@app.get("/")
def read_root():
    """Serve the web UI. The API docs remain available at /docs."""
    return FileResponse(_INDEX_HTML)


@app.get("/health")
def health_check():
    return {"status": "ok"}


def _record_stats(endpoint: str, result: dict) -> None:
    metrics = result.get("metrics", {})
    latency_s = metrics.get("latency_s") or result.get("latency_s") or 0
    stats.record(
        endpoint,
        result.get("status", "error"),
        tokens=metrics.get("total_tokens", 0) or 0,
        latency_ms=int(latency_s * 1000),
    )


@app.post("/recommend", dependencies=[Depends(require_api_key)])
@limiter.limit(settings.rate_limit)
@limiter.limit(settings.rate_limit_daily)
def recommend_books(request: Request, body: MoodRequest):
    result = agent_handler(body.mood)
    _record_stats("recommend", result)
    if result.get("status") == "error":
        return JSONResponse(status_code=502, content=result)
    return result


@app.post("/journey", dependencies=[Depends(require_api_key)])
@limiter.limit(settings.rate_limit)
@limiter.limit(settings.rate_limit_daily)
def mood_journey(request: Request, body: JourneyRequest):
    result = journey_handler(body.current_mood, body.desired_mood)
    _record_stats("journey", result)
    if result.get("status") == "error":
        return JSONResponse(status_code=502, content=result)
    return result


_stats_header = APIKeyHeader(name="X-Stats-Token", auto_error=False)


@app.get("/stats")
def get_stats(token: str | None = Security(_stats_header)):
    # Hidden unless a stats token is configured and matches (404 avoids leaking it).
    if not settings.stats_token or token != settings.stats_token:
        raise HTTPException(status_code=404, detail="Not found")
    return stats.snapshot()
