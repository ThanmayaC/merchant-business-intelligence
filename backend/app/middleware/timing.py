"""
timing.py — middleware that logs every request and how long it took.

CONCEPT — Middleware:
  Code that wraps EVERY request, like a security guard at the building
  entrance: it sees each visitor coming in and going out.
  Here it starts a stopwatch, lets the request through (call_next),
  then logs "GET /api/analytics/summary -> 200 in 12.3 ms".
"""

import time

from fastapi import Request

from app.utils.logger import logger


async def timing_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)          # run the actual route
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time-ms"] = f"{elapsed_ms:.1f}"
    logger.info("%s %s -> %d in %.1f ms", request.method, request.url.path, response.status_code, elapsed_ms)
    return response
