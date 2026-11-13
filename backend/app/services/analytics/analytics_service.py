"""
analytics_service.py — the business numbers (totals, success rate,
top merchants, failure reasons).

CONCEPT — letting the DATABASE do the math:
  We could load all 600 rows into Python and loop. But databases are
  built for counting and summing. So we write the query with SQLAlchemy
  and Postgres returns only the small answer.
  ANALOGY: Ask the librarian "how many books by X?" instead of carrying
  the whole library home to count yourself.

Reading SQLAlchemy 2.0 queries (each line maps to SQL):
  select(...)        -> SELECT ...
  .join(...)         -> JOIN ...
  .where(...)        -> WHERE ...
  .group_by(...)     -> GROUP BY ...
  .order_by(...)     -> ORDER BY ...
  func.count / sum   -> COUNT() / SUM()
  case(...)          -> CASE WHEN ... THEN ... ELSE ... END
"""

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models import Merchant, Transaction

# Reusable SQL pieces:
# 1 if the row is a success else 0, so SUM(...) = number of successes.
_IS_SUCCESS = case((Transaction.status == "SUCCESS", 1), else_=0)
# The amount if the row is a success else 0, so SUM(...) = successful money.
_SUCCESS_AMOUNT = case((Transaction.status == "SUCCESS", Transaction.amount_inr), else_=0)


def _pct(part: float, whole: float) -> float:
    """Percentage rounded to 2 decimals; safe when whole is 0."""
    return round(100.0 * part / whole, 2) if whole else 0.0


def get_summary(db: Session) -> dict:
    """Overall totals for the whole dataset."""
    stmt = select(
        func.count(Transaction.transaction_id),
        func.coalesce(func.sum(_IS_SUCCESS), 0),
        func.coalesce(func.sum(Transaction.amount_inr), 0),
        func.coalesce(func.sum(_SUCCESS_AMOUNT), 0),
    )
    # .one() = "I expect exactly one row back" (aggregates return one row).
    total, successes, volume, success_volume = db.execute(stmt).one()

    return {
        "total_transactions": total,
        "successful_transactions": int(successes),
        "failed_transactions": total - int(successes),
        "success_rate_pct": _pct(successes, total),
        "total_volume_inr": round(float(volume), 2),
        "successful_volume_inr": round(float(success_volume), 2),
    }


def get_merchant_success_rates(db: Session) -> list[dict]:
    """Success rate per merchant, lowest first (problems on top)."""
    stmt = (
        select(
            Merchant.merchant_id,
            Merchant.merchant_name,
            func.count(Transaction.transaction_id).label("total"),
            func.sum(_IS_SUCCESS).label("successes"),
        )
        .join(Transaction, Transaction.merchant_id == Merchant.merchant_id)
        .group_by(Merchant.merchant_id, Merchant.merchant_name)
    )

    rows = [
        {
            "merchant_id": r.merchant_id,
            "merchant_name": r.merchant_name,
            "total_transactions": r.total,
            "successful_transactions": int(r.successes),
            "success_rate_pct": _pct(r.successes, r.total),
        }
        for r in db.execute(stmt)
    ]
    return sorted(rows, key=lambda r: r["success_rate_pct"])


def get_top_merchants(db: Session, limit: int = 5) -> list[dict]:
    """Merchants ranked by SUCCESSFUL volume (money that actually moved)."""
    success_volume = func.sum(_SUCCESS_AMOUNT).label("success_volume")
    stmt = (
        select(
            Merchant.merchant_id,
            Merchant.merchant_name,
            Merchant.category,
            func.count(Transaction.transaction_id).label("txn_count"),
            success_volume,
        )
        .join(Transaction, Transaction.merchant_id == Merchant.merchant_id)
        .group_by(Merchant.merchant_id, Merchant.merchant_name, Merchant.category)
        .order_by(success_volume.desc())
        .limit(limit)
    )
    return [
        {
            "merchant_id": r.merchant_id,
            "merchant_name": r.merchant_name,
            "category": r.category,
            "transaction_count": r.txn_count,
            "successful_volume_inr": round(float(r.success_volume), 2),
        }
        for r in db.execute(stmt)
    ]


def get_failure_reasons(db: Session) -> list[dict]:
    """How many failed payments per failure reason, most common first."""
    count = func.count(Transaction.transaction_id).label("count")
    stmt = (
        select(Transaction.failure_reason, count)
        .where(Transaction.status == "FAILED")
        .group_by(Transaction.failure_reason)
        .order_by(count.desc())
    )
    rows = db.execute(stmt).all()
    total_failed = sum(r.count for r in rows)
    return [
        {
            "failure_reason": r.failure_reason or "UNKNOWN",
            "count": r.count,
            "share_pct": _pct(r.count, total_failed),
        }
        for r in rows
    ]
