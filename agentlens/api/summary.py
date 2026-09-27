"""Summary API endpoint."""
from fastapi import APIRouter
from agentlens.models import Summary, AnalysisResult, Session
from agentlens.dataset.generator import generate_dataset
from agentlens.backend.analyzer import analyze_all_sessions
from agentlens.backend.detectors import (
    detect_unsupported_success_claim,
    detect_repeated_question,
    detect_no_progress_search,
    detect_wrong_customer_record,
    detect_incomplete_request,
)

router = APIRouter()
_cache: dict | None = None


def _get_data():
    global _cache
    if _cache is None:
        data = generate_dataset()
        sessions = [Session(**s) for s in data]
        analyses, summary = analyze_all_sessions(sessions)
        _cache = {"analyses": analyses, "summary": summary}
    return _cache["analyses"], _cache["summary"]


@router.get("/summary", response_model=Summary)
async def get_summary():
    _, summary = _get_data()
    return Summary(
        total_sessions=summary["total_sessions"],
        successful=summary["successful"],
        recovered=summary["recovered"],
        likely_failures=summary["likely_failures"],
        ambiguous=summary["ambiguous"],
        total_findings=summary["total_findings"],
        findings_by_type=summary["findings_by_type"],
    )


@router.get("/issues")
async def get_issues():
    analyses, _ = _get_data()
    from collections import defaultdict
    type_data = defaultdict(lambda: {"count": 0, "confidences": [], "sessions": [], "descriptions": set()})
    for analysis in analyses:
        for finding in analysis.findings:
            td = type_data[finding.type]
            td["count"] += 1
            td["confidences"].append(finding.confidence)
            td["sessions"].append(analysis.session_id)
            td["descriptions"].add(finding.reason[:80])

    severity_map = {
        "UNSUPPORTED_SUCCESS_CLAIM": "high",
        "WRONG_CUSTOMER_RECORD": "high",
        "INCOMPLETE_REQUEST": "high",
        "REPEATED_QUESTION": "medium",
        "NO_PROGRESS_SEARCH": "medium",
        "AMBIGUOUS_CASE": "low",
    }
    descriptions = {
        "UNSUPPORTED_SUCCESS_CLAIM": "Agent claims a task is complete when tools indicate it is still pending.",
        "REPEATED_QUESTION": "Agent asks users to re-provide information they already shared.",
        "NO_PROGRESS_SEARCH": "Agent performs repeated searches that yield no new results.",
        "WRONG_CUSTOMER_RECORD": "Agent retrieves or references a different customer's data.",
        "INCOMPLETE_REQUEST": "Agent completes only part of a multi-part user request.",
        "AMBIGUOUS_CASE": "Evidence is insufficient for automated classification.",
    }
    action_map = {
        "UNSUPPORTED_SUCCESS_CLAIM": "Add validation between agent claims and tool results.",
        "REPEATED_QUESTION": "Implement conversation context tracking.",
        "NO_PROGRESS_SEARCH": "Add search strategy rotation logic.",
        "WRONG_CUSTOMER_RECORD": "Add customer ID verification.",
        "INCOMPLETE_REQUEST": "Parse multi-part requests and track completion.",
        "AMBIGUOUS_CASE": "Route to human reviewers.",
    }
    groups = []
    for ftype, td in type_data.items():
        avg_conf = sum(td["confidences"]) / len(td["confidences"]) if td["confidences"] else 0.0
        groups.append({
            "type": ftype,
            "count": td["count"],
            "severity": severity_map.get(ftype, "low"),
            "avg_confidence": round(avg_conf, 2),
            "sessions": td["sessions"][:10],
            "description": descriptions.get(ftype, ""),
            "recommended_action": action_map.get(ftype, ""),
        })
    groups.sort(key=lambda g: ({"high": 0, "medium": 1, "low": 2}.get(g["severity"], 3), -g["count"]))
    return {"issues": groups}


@router.get("/metrics")
async def get_metrics():
    analyses, summary = _get_data()
    total_time = summary["total_processing_time_ms"]
    avg_time = round(total_time / len(analyses), 2) if analyses else 0
    total_events = summary["total_events"]
    throughput = round(len(analyses) / (total_time / 60000), 2) if total_time > 0 else 0
    return {
        "sessions_analyzed": summary["total_sessions"],
        "total_events_analyzed": summary["total_events"],
        "ai_analyses_count": summary["total_ai_analyses"],
        "processing_time_ms": total_time,
        "average_processing_time_ms": avg_time,
        "estimated_ai_cost": summary["estimated_ai_cost"],
        "throughput_sessions_per_min": throughput,
    }
