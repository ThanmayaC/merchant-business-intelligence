"""
data_routes.py — seeding + analytics endpoints.

  POST /api/seed                            load CSVs into PostgreSQL
  GET  /api/analytics/summary               totals + overall success rate
  GET  /api/analytics/merchant-success-rates
  GET  /api/analytics/top-merchants?limit=5
  GET  /api/analytics/failure-reasons
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.controllers import data_controller
from app.schemas.analytics import (
    FailureReasonCount,
    MerchantSuccessRate,
    SeedResponse,
    SummaryResponse,
    TopMerchant,
)

router = APIRouter(prefix="/api", tags=["Data & Analytics"])


# POST because it CHANGES data (GET should only read).
@router.post("/seed", response_model=SeedResponse)
def seed(db: Session = Depends(get_db)):
    return data_controller.seed(db)


@router.get("/analytics/summary", response_model=SummaryResponse)
def summary(db: Session = Depends(get_db)):
    return data_controller.summary(db)


@router.get("/analytics/merchant-success-rates", response_model=list[MerchantSuccessRate])
def merchant_success_rates(db: Session = Depends(get_db)):
    return data_controller.merchant_success_rates(db)


# Query(5, ge=1, le=12): ?limit= is optional, default 5, must be 1..12.
# Send ?limit=50 and FastAPI answers 422 for you, no extra code needed.
@router.get("/analytics/top-merchants", response_model=list[TopMerchant])
def top_merchants(limit: int = Query(5, ge=1, le=12), db: Session = Depends(get_db)):
    return data_controller.top_merchants(db, limit)


@router.get("/analytics/failure-reasons", response_model=list[FailureReasonCount])
def failure_reasons(db: Session = Depends(get_db)):
    return data_controller.failure_reasons(db)
