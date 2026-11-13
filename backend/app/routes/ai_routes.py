"""
ai_routes.py — document search + AI chat endpoints.

  GET  /api/search?q=...&top_k=3   compare BM25 vs dense vs hybrid (RRF)
  POST /api/chat  {"question": "..."}
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.controllers import ai_controller
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.search import SearchResponse

router = APIRouter(prefix="/api", tags=["AI"])


@router.get("/search", response_model=SearchResponse)
def search(q: str = Query(..., min_length=2), top_k: int = Query(3, ge=1, le=10)):
    return ai_controller.search(q, top_k)


# `body: ChatRequest`: FastAPI reads the JSON body and validates it with
# Pydantic BEFORE our code runs. A bad body gets a 422 automatically.
@router.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest, db: Session = Depends(get_db)):
    return ai_controller.chat(db, body.question)
