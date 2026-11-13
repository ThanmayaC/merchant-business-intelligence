"""
data_controller.py — controllers for seeding and analytics.
They call the services and turn database failures into clean HTTP errors.
"""

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.services.analytics import analytics_service
from app.services.ingestion.seed_service import seed_database
from app.utils.logger import logger


def _db_error(err: Exception) -> HTTPException:
    logger.error("Database error: %s", err)
    return HTTPException(status_code=503, detail="Database error. Is PostgreSQL running and seeded?")


def seed(db: Session) -> dict:
    try:
        return seed_database(db)
    except SQLAlchemyError as err:
        db.rollback()  # undo the half-finished work
        raise _db_error(err)


def summary(db: Session) -> dict:
    try:
        return analytics_service.get_summary(db)
    except SQLAlchemyError as err:
        raise _db_error(err)


def merchant_success_rates(db: Session) -> list[dict]:
    try:
        return analytics_service.get_merchant_success_rates(db)
    except SQLAlchemyError as err:
        raise _db_error(err)


def top_merchants(db: Session, limit: int) -> list[dict]:
    try:
        return analytics_service.get_top_merchants(db, limit)
    except SQLAlchemyError as err:
        raise _db_error(err)


def failure_reasons(db: Session) -> list[dict]:
    try:
        return analytics_service.get_failure_reasons(db)
    except SQLAlchemyError as err:
        raise _db_error(err)
