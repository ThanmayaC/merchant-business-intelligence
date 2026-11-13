"""
analytics.py (schemas) — the SHAPE of data our API sends back.

CONCEPT — Pydantic models vs ORM models:
  * ORM model (app/models)    = shape of data INSIDE the database.
  * Pydantic schema (here)    = shape of data going IN/OUT of the API.

ANALOGY: The ORM model is the warehouse shelf; the Pydantic schema is the
delivery box. FastAPI packs every response into this box, checks every
field has the right type, and also shows the box design in /docs.
"""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    database: str
    ollama: str


class SeedResponse(BaseModel):
    merchants_loaded: int
    transactions_loaded: int


class SummaryResponse(BaseModel):
    total_transactions: int
    successful_transactions: int
    failed_transactions: int
    success_rate_pct: float
    total_volume_inr: float
    successful_volume_inr: float


class MerchantSuccessRate(BaseModel):
    merchant_id: str
    merchant_name: str
    total_transactions: int
    successful_transactions: int
    success_rate_pct: float


class TopMerchant(BaseModel):
    merchant_id: str
    merchant_name: str
    category: str
    transaction_count: int
    successful_volume_inr: float


class FailureReasonCount(BaseModel):
    failure_reason: str
    count: int
    share_pct: float
