"""
Importing both models here makes sure SQLAlchemy "sees" every table
before we ask it to create them (Base.metadata.create_all).
"""

from app.models.merchant import Merchant
from app.models.transaction import Transaction

__all__ = ["Merchant", "Transaction"]
