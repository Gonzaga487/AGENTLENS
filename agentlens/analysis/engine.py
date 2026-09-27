"""Analysis engine - delegates to backend module."""
from __future__ import annotations

from agentlens.backend.analyzer import analyze_session, analyze_all_sessions, classify_session
from agentlens.backend.detectors import (
    detect_unsupported_success_claim,
    detect_repeated_question,
    detect_no_progress_search,
    detect_wrong_customer_record,
    detect_incomplete_request,
)

# Re-export for backwards compatibility
__all__ = [
    'analyze_session',
    'analyze_all_sessions',
    'classify_session',
    'detect_unsupported_success_claim',
    'detect_repeated_question',
    'detect_no_progress_search',
    'detect_wrong_customer_record',
    'detect_incomplete_request',
]
