"""Backend analysis module for AGENTLENS Phase 2.

Contains classify_session, analyze_session, and batch analysis functions.
"""
from __future__ import annotations

import time
from typing import Optional

from agentlens.models import Finding, Evidence, AnalysisResult, Session
from agentlens.backend.detectors import (
    detect_unsupported_success_claim,
    detect_repeated_question,
    detect_no_progress_search,
    detect_wrong_customer_record,
    detect_incomplete_request,
    detect_recovery,
)

AI_COST_PER_ANALYSIS = 0.0001


def _now_ms() -> float:
    return time.time() * 1000


def classify_session(session: Session, findings: list[Finding]) -> tuple[str, float]:
    """Classify session as SUCCESSFUL, RECOVERED, LIKELY_FAILURE, or AMBIGUOUS."""
    if not findings:
        had_empty_search = False
        had_success_after = False
        for msg in session.messages:
            if msg.role != "tool" or msg.tool_call is None:
                continue
            r = msg.tool_call.result
            if r.get("total", 1) == 0 or not r.get("results"):
                had_empty_search = True
            if r.get("status") == "COMPLETED" or r.get("status") == "delivered":
                had_success_after = True
        if had_empty_search and had_success_after:
            return "RECOVERED", 0.85
        return "SUCCESSFUL", 0.95

    classifications = [f.classification for f in findings]
    if "LIKELY_FAILURE" in classifications:
        for msg in session.messages:
            if msg.role == "tool" and msg.tool_call:
                r = msg.tool_call.result
                if r.get("status") == "COMPLETED" or r.get("status") == "delivered":
                    return "RECOVERED", 0.85
        return "LIKELY_FAILURE", 0.90

    if "AMBIGUOUS" in classifications:
        return "AMBIGUOUS", 0.55

    if len(classifications) > 1:
        return "AMBIGUOUS", 0.60

    return "LIKELY_FAILURE", 0.85


def analyze_session(session: Session) -> AnalysisResult:
    """Analyze a single session: run all detectors, classify, return result."""
    start = _now_ms()
    ai_analyses = 0

    detectors = [
        detect_unsupported_success_claim,
        detect_repeated_question,
        detect_no_progress_search,
        detect_wrong_customer_record,
        detect_incomplete_request,
    ]

    all_findings = []
    for detector in detectors:
        finding = detector(session)
        if finding:
            all_findings.append(finding)

    # Check for ambiguous cases (escalated sessions)
    if not all_findings and session.status == "escalated":
        ai_analyses += 1
        all_findings.append(Finding(
            type="AMBIGUOUS_CASE",
            classification="AMBIGUOUS",
            confidence=0.55,
            reason="Evidence is insufficient for automated classification.",
            evidence=[Evidence(
                message_index=0,
                message_role="assistant",
                message_content="Session requires human judgment.",
                detail="Ambiguous session: insufficient evidence"
            )],
            recommended_action="Recommend human review.",
            session_id=session.id,
            message_indices=[]
        ))

    classification, confidence = classify_session(session, all_findings)
    estimated_cost = round(ai_analyses * AI_COST_PER_ANALYSIS, 6) if ai_analyses > 0 else 0.0
    processing_time = round(_now_ms() - start, 2)

    return AnalysisResult(
        session_id=session.id,
        findings=all_findings,
        classification=classification,
        overall_confidence=confidence,
        processing_time_ms=processing_time,
        ai_analyses_count=ai_analyses,
        estimated_ai_cost=estimated_cost
    )


def analyze_all_sessions(sessions: list[Session]) -> tuple[list[AnalysisResult], dict]:
    """Analyze all sessions and return results + summary."""
    analyses = []
    total_events = 0
    total_ai = 0
    total_time = 0.0

    for session in sessions:
        result = analyze_session(session)
        analyses.append(result)
        total_events += len(session.messages)
        total_ai += result.ai_analyses_count
        total_time += result.processing_time_ms

    counts = {"SUCCESSFUL": 0, "RECOVERED": 0, "LIKELY_FAILURE": 0, "AMBIGUOUS": 0}
    findings_by_type = {}
    for a in analyses:
        counts[a.classification] += 1
        for f in a.findings:
            findings_by_type[f.type] = findings_by_type.get(f.type, 0) + 1

    summary = {
        "total_sessions": len(sessions),
        "successful": counts["SUCCESSFUL"],
        "recovered": counts["RECOVERED"],
        "likely_failures": counts["LIKELY_FAILURE"],
        "ambiguous": counts["AMBIGUOUS"],
        "total_findings": sum(len(a.findings) for a in analyses),
        "findings_by_type": findings_by_type,
        "total_events": total_events,
        "total_ai_analyses": total_ai,
        "total_processing_time_ms": round(total_time, 2),
        "estimated_ai_cost": round(total_ai * AI_COST_PER_ANALYSIS, 6),
    }

    return analyses, summary
