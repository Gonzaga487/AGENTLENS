"""Backend detection module for AGENTLENS Phase 2.

Each detector function takes a Session and returns a Finding or None.
Every finding contains: type, confidence, reason, evidence.
"""
from __future__ import annotations

import re
from typing import Optional

from agentlens.models import Finding, Evidence, Session


def detect_unsupported_success_claim(session: Session) -> Optional[Finding]:
    """Detect agent claims completion while tool result says PENDING/PROCESSING/FAILED."""
    for i, msg in enumerate(session.messages):
        if msg.role != "assistant" or msg.tool_call is not None:
            continue
        content_lower = msg.content.lower()
        claim_words = ["completed", "done", "refunded", "cancelled", "processed", "finished"]
        if not any(w in content_lower for w in claim_words):
            continue
        # Find most recent tool result before this message
        for j in range(i - 1, -1, -1):
            prev = session.messages[j]
            if prev.role == "tool" and prev.tool_call:
                result = prev.tool_call.result
                for key, val in result.items():
                    val_str = str(val).upper()
                    if "PENDING" in val_str or "PROCESSING" in val_str or "IN_PROGRESS" in val_str or "FAILED" in val_str:
                        return Finding(
                            type="UNSUPPORTED_SUCCESS_CLAIM",
                            classification="LIKELY_FAILURE",
                            confidence=0.94,
                            reason=f"Agent claimed completion while tool shows {key}={val}.",
                            evidence=[Evidence(
                                message_index=i,
                                message_role="assistant",
                                message_content=msg.content,
                                tool_result=result,
                                detail=f"Agent said: {msg.content} | Tool result: {key}={val}"
                            )],
                            recommended_action="Verify actual status through the tool before notifying the user.",
                            session_id=session.id,
                            message_indices=[i]
                        )
                break
    return None


def detect_repeated_question(session: Session) -> Optional[Finding]:
    """Detect agent asking the same or substantially similar question repeatedly."""
    user_provided = set()
    for um in session.messages:
        if um.role == "user":
            ids_found = re.findall(r'CUST-\d+|ORD-\d+', um.content)
            user_provided.update(ids_found)

    seen_questions = {}
    for i, msg in enumerate(session.messages):
        if msg.role != "assistant":
            continue
        content = msg.content.lower()
        for iid in user_provided:
            if iid.lower() in content and ("what is" in content or "can you tell" in content or "can you" in content or "please provide" in content):
                key = iid.lower()
                if key in seen_questions:
                    return Finding(
                        type="REPEATED_QUESTION",
                        classification="LIKELY_FAILURE",
                        confidence=0.91,
                        reason=f"Agent asked for '{iid}' a second time after the user already provided it.",
                        evidence=[Evidence(
                            message_index=i,
                            message_role="assistant",
                            message_content=msg.content,
                            detail=f"Repeated question for '{iid}'. First asked at message {seen_questions[key]}."
                        )],
                        recommended_action="Cache user-provided data and check conversation context before asking again.",
                        session_id=session.id,
                        message_indices=[i]
                    )
                seen_questions[key] = i
    return None


def detect_no_progress_search(session: Session) -> Optional[Finding]:
    """Detect repeated searches returning no new information."""
    empty_searches = []
    for i, msg in enumerate(session.messages):
        if msg.role != "tool" or msg.tool_call is None:
            continue
        tc = msg.tool_call
        if tc.tool_name not in ("search", "search_orders"):
            continue
        result = tc.result
        if result.get("total", 1) == 0 or not result.get("results"):
            empty_searches.append((i, result))

    if len(empty_searches) >= 3:
        return Finding(
            type="NO_PROGRESS_SEARCH",
            classification="LIKELY_FAILURE",
            confidence=0.89,
            reason=f"Agent performed {len(empty_searches)} searches, all returning zero results without changing query strategy.",
            evidence=[Evidence(
                message_index=idx,
                message_role="tool",
                message_content=session.messages[idx].content,
                tool_result=result,
                detail=f"Empty search result #{idx_idx + 1}"
            ) for idx_idx, (idx, result) in enumerate(empty_searches)],
            recommended_action="Change search strategy, use different keywords, or escalate after repeated failures.",
            session_id=session.id,
            message_indices=[idx for idx, _ in empty_searches]
        )
    return None


def detect_wrong_customer_record(session: Session) -> Optional[Finding]:
    """Detect when retrieved customer/record differs from the requested one."""
    for i, msg in enumerate(session.messages):
        if msg.role != "tool" or msg.tool_call is None:
            continue
        tc = msg.tool_call
        result = tc.result
        if "customer_id" in result and "customer_id" in tc.arguments:
            requested = str(tc.arguments["customer_id"])
            retrieved = str(result["customer_id"])
            if requested != retrieved:
                return Finding(
                    type="WRONG_CUSTOMER_RECORD",
                    classification="LIKELY_FAILURE",
                    confidence=0.96,
                    reason=f"Retrieved record for '{retrieved}' when user requested '{requested}'.",
                    evidence=[Evidence(
                        message_index=i,
                        message_role="tool",
                        message_content=msg.content,
                        tool_result=result,
                        detail=f"Requested {requested} but got {retrieved}"
                    )],
                    recommended_action="Verify customer ID matching logic. Retrieved record does not belong to requesting user.",
                    session_id=session.id,
                    message_indices=[i]
                )
    return None


def detect_incomplete_request(session: Session) -> Optional[Finding]:
    """Detect agent completing only part of a multi-step request but claiming everything done."""
    for i, msg in enumerate(session.messages):
        if msg.role != "user":
            continue
        content = msg.content.lower()
        has_multiple = any(w in content for w in [" and ", " then ", " also ", " plus ", " and then "])
        if not has_multiple or not any(w in content for w in ["cancel", "refund", "return", "process", "update", "cancel and"]):
            continue
        tool_names_done = set()
        for j in range(i + 1, len(session.messages)):
            m = session.messages[j]
            if m.role == "tool" and m.tool_call:
                tool_names_done.add(m.tool_call.tool_name)

        expected_actions = []
        if "cancel" in content:
            expected_actions.append("cancel")
        if "refund" in content:
            expected_actions.append("refund")
        if "return" in content:
            expected_actions.append("return")

        if expected_actions and len(tool_names_done) < len(expected_actions):
            return Finding(
                type="INCOMPLETE_REQUEST",
                classification="LIKELY_FAILURE",
                confidence=0.92,
                reason=f"User requested {expected_actions} but agent only performed {list(tool_names_done)}.",
                evidence=[Evidence(
                    message_index=i,
                    message_role="user",
                    message_content=msg.content,
                    detail=f"Expected {expected_actions}, got {list(tool_names_done)}"
                )],
                recommended_action="Complete ALL requested actions or explicitly inform user which parts are pending.",
                session_id=session.id,
                message_indices=[i]
            )
    return None


def detect_recovery(session: Session) -> Optional[Finding]:
    """Detect failed attempts followed by successful recovery.
    Returns None (no finding) but influences classification as RECOVERED."""
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
    # Recovery is not a finding — it's a classification signal
    return None
