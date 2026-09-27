"""AGENTLENS - AI Agent Reliability Intelligence.

Main FastAPI application.

Phase 1: Core backend with deterministic failure detection,
synthetic dataset, and dashboard API.
"""
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from .api.health import router as health_router
from .api.sessions import router as sessions_router
from .api.summary import router as summary_router

from .models import Session
from .dataset.generator import generate_dataset

# Build the dataset on startup
_all_sessions = [Session(**s) for s in generate_dataset()]

app = FastAPI(
    title="AGENTLENS",
    description="AI Agent Reliability Intelligence - See where AI agents fail. Prove why.",
    version="1.0.0",
)

# CORS for frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health_router, prefix="/api")
app.include_router(sessions_router, prefix="/api")
app.include_router(summary_router, prefix="/api")

# ─── Paths ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "agentlens", "static")


# ─── Serve Frontend ────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Serve the dashboard."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    return FileResponse(index_path)


# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("agentlens.main:app", host="127.0.0.1", port=8000, reload=True)
