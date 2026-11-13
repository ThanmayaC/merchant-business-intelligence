"""
health_routes.py — GET /health

CONCEPT — FastAPI:
  A Python web framework (like Express for Node). You write normal
  functions; decorators like @router.get("/path") turn them into endpoints.
  FastAPI then uses the TYPE HINTS to:
    * read and validate inputs (query params, JSON bodies),
    * validate outputs against `response_model` (a Pydantic schema),
    * auto-generate interactive docs at http://localhost:8000/docs

CONCEPT — Dependency Injection, `Depends(get_db)`:
  "Before running this function, call get_db() and pass me its result."
  So every route gets a fresh DB session and it is always closed after.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.controllers import health_controller
from app.schemas.analytics import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)):
    return health_controller.check_health(db)
