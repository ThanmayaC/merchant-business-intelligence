"""
health_controller.py — "is everything plugged in?"

ROUTE vs CONTROLLER vs SERVICE (same pattern as Express):
  route      = the URL + HTTP method (the door)
  controller = handles the HTTP side: inputs, errors, status codes (the receptionist)
  service    = the real business logic, knows nothing about HTTP (the expert)
"""

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.services.assistant import ollama_client


def check_health(db: Session) -> dict:
    try:
        db.execute(text("SELECT 1"))  # cheapest possible query: "are you there?"
        database = "connected"
    except SQLAlchemyError:
        database = "unreachable"

    ollama = "connected" if ollama_client.is_available() else "unreachable"
    status = "ok" if database == "connected" else "degraded"
    return {"status": status, "database": database, "ollama": ollama}
