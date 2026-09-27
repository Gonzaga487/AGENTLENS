"""Health check endpoint."""
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "AGENTLENS",
        "version": "1.0.0",
        "api": "AI Agent Reliability Intelligence"
    }
