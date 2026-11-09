from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from agent import agent_handler

app = FastAPI(title="Agent Bibliothécaire de l'Humeur")

class MoodRequest(BaseModel):
    mood: str

@app.get("/")
def read_root():
    """Redirige automatiquement la page d'accueil vers l'interface de test (Swagger)."""
    return RedirectResponse(url="/docs")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/recommend")
def recommend_books(request: MoodRequest):
    return agent_handler(request.mood)