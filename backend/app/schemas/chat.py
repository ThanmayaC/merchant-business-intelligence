"""
chat.py (schemas) — what the chat page SENDS and what it RECEIVES.

Field(...) adds validation rules. If the React app sends an empty
question, Pydantic rejects it with a 422 error automatically. We never
write that `if` check ourselves.
"""

from typing import Any

from pydantic import BaseModel, Field

from app.schemas.search import SearchHit


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=500)


class ChatResponse(BaseModel):
    answer: str
    route: str                      # "analytics", "documents" or "both"
    analytics_metric: str | None     # which analytics tool was used (if any)
    analytics_data: Any | None       # the raw numbers the AI saw
    sources: list[SearchHit]         # the document passages the AI saw
