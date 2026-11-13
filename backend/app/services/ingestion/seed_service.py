"""
seed_service.py — loads the CSV files into PostgreSQL.

ANALOGY: The CSV files are boxes of paper receipts. This service unpacks
the boxes (Pandas), turns each paper into a Python object (ORM model),
and files them into the database cabinet (Session).

It is safe to run many times: it empties the tables first, then reloads.
"""

from decimal import Decimal

import pandas as pd
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models import Merchant, Transaction
from app.utils.logger import logger


def _clean(value):
    """Pandas writes empty CSV cells as NaN ("not a number"). The DB wants None (NULL)."""
    return None if pd.isna(value) else value


def seed_database(db: Session) -> dict:
    raw_dir = settings.data_dir / "raw"

    # 1) READ — Pandas turns each CSV into a DataFrame (an in-memory table).
    merchants_df = pd.read_csv(raw_dir / "merchants.csv")
    transactions_df = pd.read_csv(raw_dir / "transactions.csv")

    # Convert the timestamp text "2026-10-08 08:25:00" into real datetime values.
    transactions_df["transaction_timestamp"] = pd.to_datetime(
        transactions_df["transaction_timestamp"]
    )

    # 2) EMPTY — delete children (transactions) before parents (merchants),
    #    otherwise the foreign key would complain about orphan receipts.
    db.execute(delete(Transaction))
    db.execute(delete(Merchant))

    # 3) BUILD ORM OBJECTS — one Python object per CSV row.
    merchants = [
        Merchant(
            merchant_id=row.merchant_id,
            merchant_name=row.merchant_name,
            category=row.category,
            city=row.city,
        )
        for row in merchants_df.itertuples(index=False)
    ]

    # Note: the CSV also has merchant_name, but we DON'T store it twice.
    # The foreign key merchant_id already points to the merchant row
    # (this is called "normalisation").
    transactions = [
        Transaction(
            transaction_id=row.transaction_id,
            merchant_id=row.merchant_id,
            transaction_timestamp=row.transaction_timestamp.to_pydatetime(),
            amount_inr=Decimal(str(row.amount_inr)),
            status=row.status,
            payment_method=row.payment_method,
            bank_name=row.bank_name,
            failure_reason=_clean(row.failure_reason),
            city=row.city,
        )
        for row in transactions_df.itertuples(index=False)
    ]

    # 4) SAVE — add_all stages them; commit() writes them permanently.
    #    If anything fails before commit, nothing is half-saved.
    db.add_all(merchants)
    db.flush()  # send merchants first so the foreign keys can find them
    db.add_all(transactions)
    db.commit()

    logger.info("Seeded %d merchants and %d transactions", len(merchants), len(transactions))
    return {"merchants_loaded": len(merchants), "transactions_loaded": len(transactions)}
