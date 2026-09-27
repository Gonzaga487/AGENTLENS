"""Session API endpoints."""
from fastapi import APIRouter, HTTPException
from typing import Optional

from agentlens.models import Session, AnalysisResult
from agentlens.dataset.generator import generate_dataset
from agentlens.backend.analyzer import analyze_session, analyze_all_sessions

router = APIRouter()

_sessions_cache: list[Session] | None = None
_analyses_cache: list[AnalysisResult] | None = None


def _get_sessions() -> list[Session]:
    global _sessions_cache
    if _sessions_cache is None:
        data = generate_dataset()
        _sessions_cache = [Session(**s) for s in data]
    return _sessions_cache


def _get_analyses() -> tuple[list[AnalysisResult], dict]:
    global _analyses_cache
    if _analyses_cache is None:
        sessions = _get_sessions()
        analyses, summary = analyze_all_sessions(sessions)
        _analyses_cache = analyses
    return _analyses_cache, None


@router.get("/sessions", response_model=list[Session])
async def get_sessions(limit: Optional[int] = 50, offset: int = 0):
    sessions = _get_sessions()
    return sessions[offset:offset + limit]


@router.get("/sessions/{session_id}", response_model=Session)
async def get_session(session_id: str):
    sessions = _get_sessions()
    for s in sessions:
        if s.id == session_id:
            return s
    raise HTTPException(status_code=404, detail="Session not found")


@router.get("/sessions/{session_id}/analysis", response_model=AnalysisResult)
async def get_session_analysis(session_id: str):
    sessions = _get_sessions()
    target = None
    for s in sessions:
        if s.id == session_id:
            target = s
            break
    if target is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return analyze_session(target)


@router.get("/sessions/{session_id}/issues")
async def get_session_issues(session_id: str):
    result = await get_session_analysis(session_id)
    return {"session_id": session_id, "issues": [f.model_dump() for f in result.findings]}
