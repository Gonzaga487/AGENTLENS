"""Pydantic models for AGENTLENS."""
from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel, Field


# ─── Core Message Types ────────────────────────────────────────────────────────

class ToolCall(BaseModel):
    tool_name: str
    arguments: dict
    result: dict
    timestamp: str


class Message(BaseModel):
    role: Literal["user", "assistant", "tool"]
    content: str
    timestamp: str
    tool_call: Optional[ToolCall] = None


# ─── Session ───────────────────────────────────────────────────────────────────

class Session(BaseModel):
    id: str
    title: str
    customer_id: Optional[str] = None
    order_id: Optional[str] = None
    created_at: str
    messages: list[Message] = Field(default_factory=list)
    status: Literal["active", "completed", "escalated"] = "completed"


# ─── Findings ──────────────────────────────────────────────────────────────────

class Evidence(BaseModel):
    message_index: int
    message_role: str
    message_content: str
    tool_result: Optional[dict] = None
    detail: str


class Finding(BaseModel):
    type: str
    classification: Literal["SUCCESSFUL", "RECOVERED", "LIKELY_FAILURE", "AMBIGUOUS"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str
    evidence: list[Evidence] = Field(default_factory=list)
    recommended_action: str
    session_id: str
    message_indices: list[int] = Field(default_factory=list)


# ─── Analysis ──────────────────────────────────────────────────────────────────

class AnalysisResult(BaseModel):
    session_id: str
    findings: list[Finding]
    classification: Literal["SUCCESSFUL", "RECOVERED", "LIKELY_FAILURE", "AMBIGUOUS"]
    overall_confidence: float
    processing_time_ms: float
    ai_analyses_count: int = 0
    estimated_ai_cost: Optional[float] = None


# ─── Summary ───────────────────────────────────────────────────────────────────

class Summary(BaseModel):
    total_sessions: int
    successful: int
    recovered: int
    likely_failures: int
    ambiguous: int
    total_findings: int
    findings_by_type: dict[str, int] = Field(default_factory=dict)


# ─── Issues ────────────────────────────────────────────────────────────────────

class IssueGroup(BaseModel):
    type: str
    count: int
    severity: Literal["high", "medium", "low"]
    avg_confidence: float
    sessions: list[str] = Field(default_factory=list)
    description: str
    recommended_action: str


# ─── Metrics ───────────────────────────────────────────────────────────────────

class Metrics(BaseModel):
    sessions_analyzed: int
    total_events_analyzed: int
    ai_analyses_count: int
    processing_time_ms: float
    estimated_ai_cost: Optional[float] = None
    throughput_sessions_per_min: float

__all__ = ['Session', 'Message', 'ToolCall', 'Finding', 'Evidence', 'AnalysisResult', 'Summary', 'IssueGroup', 'Metrics']
