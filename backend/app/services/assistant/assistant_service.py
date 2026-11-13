"""
assistant_service.py — the "brain" of the chat page.

THE FLOW (two LLM calls):
  1. ROUTE   : the LLM reads the question and decides which tool(s) to use:
                 "analytics" -> numbers from PostgreSQL
                 "documents" -> passages from the policy docs (RAG)
                 "both"      -> both of the above
  2. GATHER  : we (normal Python, NOT the LLM) run those tools.
  3. ANSWER  : the LLM writes the final answer using ONLY that data.

ANALOGY: A receptionist (call 1) reads your request and sends it to the
accounts team (analytics) and/or the policy library (RAG). Then a writer
(call 2) turns their findings into one clear reply.

Why not let the LLM compute the numbers itself? Small LLMs are bad at
arithmetic and would invent figures. The database computes; the LLM explains.
"""

from typing import Literal

from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.services.analytics import analytics_service
from app.services.assistant import ollama_client
from app.services.rag.search_service import get_search_engine
from app.utils.logger import logger

# The analytics "tools" the router may choose from (name -> function).
ANALYTICS_TOOLS = {
    "summary": analytics_service.get_summary,
    "merchant_success_rates": analytics_service.get_merchant_success_rates,
    "top_merchants": analytics_service.get_top_merchants,
    "failure_reasons": analytics_service.get_failure_reasons,
}


# A plain-English label for each result. Small LLMs misread long raw JSON
# (e.g. picking the LAST row as "worst"), so we say exactly how it is ordered.
METRIC_LABELS = {
    "summary": "Overall totals for all transactions",
    "merchant_success_rates": "Success rate per merchant, sorted from WORST (first line) to BEST (last line)",
    "top_merchants": "Merchants ranked by successful volume, from HIGHEST (first line) down",
    "failure_reasons": "Failed payments per failure reason, from MOST common (first line) to least",
}


def _format_analytics(metric: str, data) -> str:
    """Turn the result into short readable lines: one line per row."""
    rows = data if isinstance(data, list) else [data]
    lines = [", ".join(f"{k}={v}" for k, v in row.items()) for row in rows]
    return f"ANALYTICS RESULT: {METRIC_LABELS[metric]}\n" + "\n".join(
        f"{i}. {line}" for i, line in enumerate(lines, start=1)
    )


class RouteDecision(BaseModel):
    """
    PYDANTIC validating the LLM's output. LLMs sometimes reply with
    nonsense. Literal[...] means ONLY these exact strings are allowed.
    Anything else raises ValidationError and we fall back to keyword rules.
    """
    route: Literal["analytics", "documents", "both"]
    metric: Literal["summary", "merchant_success_rates", "top_merchants", "failure_reasons"] | None = None


ROUTER_PROMPT = """You route questions for a UPI merchant business-intelligence assistant.
Tools:
- "analytics": numbers from the transaction database. Pick ONE metric:
    "summary" (total count, volume, overall success rate),
    "merchant_success_rates" (success rate of each merchant),
    "top_merchants" (merchants ranked by successful volume),
    "failure_reasons" (count of failed payments per failure reason).
- "documents": policy/guide text (onboarding policy, payment failure meanings and
  investigation steps, merchant performance review rules).
- "both": the question needs numbers AND policy text.
Reply ONLY with JSON like {"route": "analytics", "metric": "summary"}.
Use "metric": null when route is "documents".

Examples (this is called "few-shot prompting": showing the model worked examples):
Q: What is the overall success rate? -> {"route": "analytics", "metric": "summary"}
Q: Which merchant has the lowest success rate? -> {"route": "analytics", "metric": "merchant_success_rates"}
Q: Who are the top merchants? -> {"route": "analytics", "metric": "top_merchants"}
Q: What does ISSUER_DECLINED mean? -> {"route": "documents", "metric": null}
Q: What is required to onboard a merchant? -> {"route": "documents", "metric": null}
Q: What is the most common failure reason and what does it mean? -> {"route": "both", "metric": "failure_reasons"}
Q: Which merchants are below the success threshold and what should be done? -> {"route": "both", "metric": "merchant_success_rates"}"""

ANSWER_PROMPT = """You are a merchant business-intelligence assistant for a UPI payments team.
Answer the question using ONLY the context below.
- Quote numbers exactly as given; do not calculate new numbers.
- When you use a document passage, cite it like [document#section-number].
- If the context does not contain the answer, say you don't have that information.
- Keep the answer short and clear (under 150 words)."""


def _keyword_route(question: str) -> RouteDecision:
    """Backup router (no LLM) used when the LLM's JSON is invalid."""
    q = question.lower()
    wants_numbers = any(w in q for w in ["how many", "total", "rate", "top", "count", "volume", "most"])
    wants_docs = any(w in q for w in ["why", "what does", "mean", "policy", "should", "how to", "guide"])

    metric = "summary"
    if "fail" in q or "reason" in q:
        metric = "failure_reasons"
    elif "top" in q or "highest" in q or "best" in q:
        metric = "top_merchants"
    elif "merchant" in q and "rate" in q:
        metric = "merchant_success_rates"

    if wants_numbers and wants_docs:
        return RouteDecision(route="both", metric=metric)
    if wants_numbers:
        return RouteDecision(route="analytics", metric=metric)
    return RouteDecision(route="documents")


def route_question(question: str) -> RouteDecision:
    """Step 1: ask the LLM which tool(s) to use."""
    messages = [
        {"role": "system", "content": ROUTER_PROMPT},
        {"role": "user", "content": question},
    ]
    try:
        raw = ollama_client.chat(messages, json_mode=True)
        decision = RouteDecision.model_validate_json(raw)  # Pydantic checks the JSON
        if decision.route in ("analytics", "both") and decision.metric is None:
            decision.metric = "summary"
        return decision
    except (ValidationError, ValueError) as err:
        logger.warning("Router output invalid (%s); using keyword rules", err)
        return _keyword_route(question)


def answer_question(db: Session, question: str) -> dict:
    # 1) ROUTE
    decision = route_question(question)
    logger.info("Question routed to %s (metric=%s)", decision.route, decision.metric)

    # 2) GATHER — plain Python runs the chosen tools.
    analytics_data = None
    sources: list[dict] = []
    context_parts: list[str] = []

    if decision.route in ("analytics", "both"):
        analytics_data = ANALYTICS_TOOLS[decision.metric](db)
        context_parts.append(_format_analytics(decision.metric, analytics_data))

    if decision.route in ("documents", "both"):
        # 4 passages, not 3: when only ONE method finds the right chunk (e.g. dense
        # finds BANK_TIMEOUT for "payment takes too long" but BM25 can't, because
        # "receive" != "received"), RRF can place it 4th. Small chunks, so 4 is cheap.
        sources = get_search_engine().search(question, top_k=4)["hybrid_rrf"]
        passages = "\n\n".join(f"[{s['chunk_id']}] {s['text']}" for s in sources)
        context_parts.append(f"DOCUMENT PASSAGES:\n{passages}")

    # 3) ANSWER — "Augment" the prompt with the context, then "Generate".
    messages = [
        {"role": "system", "content": ANSWER_PROMPT},
        {"role": "user", "content": "CONTEXT:\n" + "\n\n".join(context_parts) + f"\n\nQUESTION: {question}"},
    ]
    answer = ollama_client.chat(messages)

    return {
        "answer": answer.strip(),
        "route": decision.route,
        "analytics_metric": decision.metric if analytics_data is not None else None,
        "analytics_data": analytics_data,
        "sources": sources,
    }
