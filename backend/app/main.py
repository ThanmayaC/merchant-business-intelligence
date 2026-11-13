"""
main.py — the ENTRY POINT. Uvicorn starts the app from here:
    uvicorn app.main:app --reload

ANALOGY: main.py is the building's main switchboard. It doesn't do the
work itself; it switches on the database tables, installs the security
guard (middleware), and connects all the doors (routers).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import app.models  # noqa: F401  (registers the tables on Base before create_all)
from app.config.database import Base, engine
from app.config.settings import PROJECT_ROOT, settings
from app.middleware.timing import timing_middleware
from app.routes import ai_routes, data_routes, health_routes
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs ONCE at startup (before `yield`) and once at shutdown (after)."""
    try:
        # Creates the tables if they don't exist yet (never deletes data).
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables are ready")
    except Exception as err:  # keep the server up so /health can report the problem
        logger.error("Could not create tables: %s", err)
    yield


app = FastAPI(
    title="Merchant Business Intelligence API",
    description="UPI merchant analytics + RAG document search + local LLM assistant",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS: browsers block a page on one origin (localhost:5173) from calling
# another (localhost:8000) unless the server says it's allowed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(timing_middleware)

app.include_router(health_routes.router)
app.include_router(data_routes.router)
app.include_router(ai_routes.router)

# PRODUCTION: after `npm run build`, the React app is plain files in frontend/dist.
# FastAPI serves them too, so the whole project runs as ONE server on port 8000.
# This is mounted LAST so /health and /api/... above always win.
# (In development the folder doesn't exist, and Vite serves React on port 5173.)
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
