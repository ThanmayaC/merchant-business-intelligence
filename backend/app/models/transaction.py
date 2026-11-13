"""
transaction.py — the `transactions` table (one row = one UPI payment).

FOREIGN KEY ANALOGY: `merchant_id` here is like writing a shop's ID on a
receipt. The receipt doesn't copy the shop's whole details; it just points
to the shop in the `merchants` table. The database refuses a receipt that
points to a shop that doesn't exist.
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(
        ForeignKey("merchants.merchant_id"), index=True, nullable=False
    )
    transaction_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Numeric(12, 2) = exact money with 2 decimals (floats can round wrongly).
    amount_inr: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    status: Mapped[str] = mapped_column(String(20), index=True, nullable=False)  # SUCCESS / FAILED
    payment_method: Mapped[str] = mapped_column(String(20), nullable=False)
    bank_name: Mapped[str] = mapped_column(String(50), nullable=False)

    # `str | None` = this column may be empty (only failed payments have a reason).
    failure_reason: Mapped[str | None] = mapped_column(String(50), nullable=True)
    city: Mapped[str] = mapped_column(String(50), nullable=False)

    # The other side of Merchant.transactions: transaction.merchant -> Merchant object.
    merchant: Mapped["Merchant"] = relationship(back_populates="transactions")
