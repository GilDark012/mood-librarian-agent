"""FastAPI entry point for the Mood Librarian agent."""
import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Request, Security
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, StringConstraints
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from agent import DISCLAIMER, agent_handler
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
    return JSONResponse(status_code=429, content={"detail": "Trop de requêtes. Réessayez plus tard."})


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


@app.get("/")
def read_root():
    """Redirect the home page to the interactive Swagger docs."""
    return RedirectResponse(url="/docs")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/recommend", dependencies=[Depends(require_api_key)])
@limiter.limit(settings.rate_limit)
def recommend_books(request: Request, body: MoodRequest):
    result = agent_handler(body.mood)
    if result.get("status") == "error":
        return JSONResponse(status_code=502, content=result)
    return result
