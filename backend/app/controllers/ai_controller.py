"""
ai_controller.py — controllers for document search (RAG) and the chat assistant.
"""

import httpx
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.services.assistant.assistant_service import answer_question
from app.services.rag.search_service import get_search_engine
from app.utils.logger import logger


def search(query: str, top_k: int) -> dict:
    return get_search_engine().search(query, top_k)


def chat(db: Session, question: str) -> dict:
    try:
        return answer_question(db, question)
    except httpx.HTTPError as err:
        logger.error("Ollama error: %s", err)
        raise HTTPException(
            status_code=503,
            detail="The AI model is not reachable. Is Ollama running with the chat model pulled?",
        )
    except SQLAlchemyError as err:
        logger.error("Database error: %s", err)
        raise HTTPException(status_code=503, detail="Database error. Is PostgreSQL running and seeded?")
