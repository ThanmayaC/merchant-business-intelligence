"""
merchant.py — the `merchants` table, written as a Python class (ORM model).

ANALOGY: This class is the BLUEPRINT of a table.
  class name   -> table
  each Column  -> a column in that table
  each object  -> one row (one merchant)

It is like a Mongoose schema, but for a SQL table with fixed columns.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database import Base


class Merchant(Base):
    __tablename__ = "merchants"

    # Mapped[str] = the Python type; mapped_column(...) = the SQL column rules.
    merchant_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    merchant_name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    city: Mapped[str] = mapped_column(String(50), nullable=False)

    # RELATIONSHIP: one merchant has MANY transactions.
    # This is not a column. It is a shortcut: merchant.transactions gives
    # you the list of Transaction objects (SQLAlchemy runs the JOIN for you).
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="merchant")
