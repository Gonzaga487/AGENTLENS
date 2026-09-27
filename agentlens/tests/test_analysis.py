"""Tests for AGENTLENS Phase 2 - backend detectors and analyzer."""
from __future__ import annotations

import pytest
from agentlens.models import Session, Message, ToolCall, Finding, Evidence
from agentlens.backend.analyzer import analyze_session, classify_session, analyze_all_sessions
from agentlens.backend.detectors import (
    detect_unsupported_success_claim,
    detect_repeated_question,
    detect_no_progress_search,
    detect_wrong_customer_record,
    detect_incomplete_request,
    detect_recovery,
)


def make_session(messages_data: list[dict]) -> Session:
    messages = []
    for md in messages_data:
        msg = Message(
            role=md['role'],
            content=md['content'],
            timestamp=md.get('timestamp', '2026-09-20T09:00:00'),
        )
        if 'tool_call' in md:
            tc = md['tool_call']
            msg.tool_call = ToolCall(
                tool_name=tc['tool_name'],
                arguments=tc['arguments'],
                result=tc['result'],
                timestamp=tc.get('timestamp', msg.timestamp),
            )
        messages.append(msg)
    return Session(id='test', title='Test', created_at='2026-09-20T09:00:00', messages=messages)


class TestUnsupportedSuccessClaim:
    def test_claim_with_pending_refund(self):
        s = make_session([
            {"role": "user", "content": "Refund status?"},
            {"role": "assistant", "content": "Let me check."},
            {"role": "tool", "content": "check",
             "tool_call": {"tool_name": "check_refund_status", "arguments": {"order_id": "ORD-1"},
                           "result": {"refund_id": "REF-1", "refund_status": "PENDING", "amount": 29.99}},
             "timestamp": "2026-09-20T09:01:00"},
            {"role": "assistant", "content": "Your refund of $29.99 has been completed!"},
        ])
        f = detect_unsupported_success_claim(s)
        assert f is not None
        assert f.type == "UNSUPPORTED_SUCCESS_CLAIM"
        assert f.classification == "LIKELY_FAILURE"
        assert f.confidence == 0.94

    def test_legitimate_completion_no_finding(self):
        s = make_session([
            {"role": "user", "content": "Refund?"},
            {"role": "tool", "content": "check",
             "tool_call": {"tool_name": "check_refund_status", "arguments": {},
                           "result": {"refund_status": "COMPLETED"}},
             "timestamp": "2026-09-20T09:01:00"},
            {"role": "assistant", "content": "Refund is completed!"},
        ])
        assert detect_unsupported_success_claim(s) is None


class TestRepeatedQuestion:
    def test_asking_for_provided_id(self):
        s = make_session([
            {"role": "user", "content": "My order is ORD-5 for CUST-100"},
            {"role": "assistant", "content": "I can help! What is your order number ORD-5?"},
            {"role": "user", "content": "My order is ORD-5."},
            {"role": "assistant", "content": "Thanks! What is your customer ID CUST-100?"},
            {"role": "user", "content": "My customer ID is CUST-100."},
            {"role": "assistant", "content": "Can you tell me your customer ID CUST-100?"},
        ])
        assert detect_repeated_question(s) is not None

    def test_no_repetition_no_finding(self):
        s = make_session([
            {"role": "user", "content": "Order ORD-5 for CUST-100"},
            {"role": "assistant", "content": "Looking up your order."},
            {"role": "tool", "content": "lookup",
             "tool_call": {"tool_name": "lookup_order", "arguments": {"order_id": "ORD-5"},
                           "result": {"order_id": "ORD-5", "customer_id": "CUST-100"}},
             "timestamp": "2026-09-20T09:01:00"},
        ])
        assert detect_repeated_question(s) is None


class TestNoProgressSearch:
    def test_five_empty_searches(self):
        msgs = [{"role": "user", "content": "Help with order"}]
        for i in range(5):
            msgs.append({"role": "assistant", "content": f"Search {i}", "timestamp": f"2026-09-20T09:{i}:00"})
            msgs.append({"role": "tool", "content": "search",
                         "tool_call": {"tool_name": "search", "arguments": {"query": "order issue"},
                                       "result": {"results": [], "total": 0}},
                         "timestamp": f"2026-09-20T09:{i}:01"})
        s = make_session(msgs)
        f = detect_no_progress_search(s)
        assert f is not None
        assert f.type == "NO_PROGRESS_SEARCH"
        assert f.confidence == 0.89
        assert len(f.evidence) >= 3

    def test_search_with_results_no_finding(self):
        s = make_session([
            {"role": "user", "content": "Help with order"},
            {"role": "tool", "content": "search",
             "tool_call": {"tool_name": "search", "arguments": {"query": "order issue"},
                           "result": {"results": [{"id": 1}], "total": 1}},
             "timestamp": "2026-09-20T09:01:00"},
        ])
        assert detect_no_progress_search(s) is None


class TestWrongCustomerRecord:
    def test_different_customer_id(self):
        s = make_session([
            {"role": "user", "content": "I'm CUST-100"},
            {"role": "tool", "content": "lookup",
             "tool_call": {"tool_name": "lookup_customer", "arguments": {"customer_id": "CUST-100"},
                           "result": {"customer_id": "CUST-999", "name": "Wrong Person"}},
             "timestamp": "2026-09-20T09:01:00"},
            {"role": "assistant", "content": "Hi! I see your account for CUST-999."},
        ])
        f = detect_wrong_customer_record(s)
        assert f is not None
        assert f.type == "WRONG_CUSTOMER_RECORD"
        assert f.confidence == 0.96
        assert "CUST-100" in f.reason

    def test_correct_customer_no_finding(self):
        s = make_session([
            {"role": "user", "content": "I'm CUST-100"},
            {"role": "tool", "content": "lookup",
             "tool_call": {"tool_name": "lookup_customer", "arguments": {"customer_id": "CUST-100"},
                           "result": {"customer_id": "CUST-100", "name": "Jane Doe"}},
             "timestamp": "2026-09-20T09:01:00"},
        ])
        assert detect_wrong_customer_record(s) is None


class TestIncompleteRequest:
    def test_cancel_and_refund_only_cancelled(self):
        s = make_session([
            {"role": "user", "content": "Cancel order ORD-1 AND refund my payment for CUST-100"},
            {"role": "assistant", "content": "Let me handle that."},
            {"role": "tool", "content": "cancel",
             "tool_call": {"tool_name": "cancel_order", "arguments": {"order_id": "ORD-1"},
                           "result": {"order_id": "ORD-1", "status": "CANCELLED"}},
             "timestamp": "2026-09-20T09:01:00"},
            {"role": "assistant", "content": "Done! Your order has been fully processed and refunded."},
        ])
        f = detect_incomplete_request(s)
        assert f is not None
        assert f.type == "INCOMPLETE_REQUEST"
        assert f.confidence == 0.92

    def test_both_actions_complete_no_finding(self):
        s = make_session([
            {"role": "user", "content": "Cancel ORD-1 AND refund for CUST-100"},
            {"role": "tool", "content": "cancel",
             "tool_call": {"tool_name": "cancel_order", "arguments": {"order_id": "ORD-1"},
                           "result": {"status": "CANCELLED"}},
             "timestamp": "2026-09-20T09:01:00"},
            {"role": "tool", "content": "refund",
             "tool_call": {"tool_name": "process_refund", "arguments": {"order_id": "ORD-1"},
                           "result": {"status": "COMPLETED"}},
             "timestamp": "2026-09-20T09:02:00"},
        ])
        assert detect_incomplete_request(s) is None


class TestRecovery:
    def test_recovered_session_classification(self):
        s = make_session([
            {"role": "user", "content": "Find order ORD-5"},
            {"role": "tool", "content": "search",
             "tool_call": {"tool_name": "search_orders", "arguments": {"query": "ORD-5"},
                           "result": {"results": [], "total": 0}},
             "timestamp": "2026-09-20T09:01:00"},
            {"role": "tool", "content": "search",
             "tool_call": {"tool_name": "search_orders", "arguments": {"query": "ORD-5"},
                           "result": {"results": [], "total": 0}},
             "timestamp": "2026-09-20T09:02:00"},
            {"role": "tool", "content": "lookup",
             "tool_call": {"tool_name": "lookup_order", "arguments": {"order_id": "ORD-5"},
                           "result": {"order_id": "ORD-5", "status": "delivered"}},
             "timestamp": "2026-09-20T09:03:00"},
        ])
        cls, conf = classify_session(s, [])
        assert cls == "RECOVERED"
        assert conf == 0.85

    def test_clean_successful_session(self):
        s = make_session([
            {"role": "user", "content": "Refund order ORD-1"},
            {"role": "tool", "content": "lookup",
             "tool_call": {"tool_name": "lookup_order", "arguments": {"order_id": "ORD-1"},
                           "result": {"order_id": "ORD-1", "total": 1}},
             "timestamp": "2026-09-20T09:01:00"},
            {"role": "tool", "content": "refund",
             "tool_call": {"tool_name": "process_refund", "arguments": {},
                           "result": {"total": 1, "status": "COMPLETED"}},
             "timestamp": "2026-09-20T09:02:00"},
        ])
        result = analyze_session(s)
        assert result.classification in ("SUCCESSFUL", "RECOVERED")
        assert len(result.findings) == 0

    def test_detect_recovery_not_a_finding(self):
        s = make_session([
            {"role": "user", "content": "Find order"},
            {"role": "tool", "content": "search",
             "tool_call": {"tool_name": "search", "arguments": {"query": "x"},
                           "result": {"results": [], "total": 0}},
             "timestamp": "2026-09-20T09:01:00"},
            {"role": "tool", "content": "lookup",
             "tool_call": {"tool_name": "lookup_order", "arguments": {"order_id": "ORD-1"},
                           "result": {"status": "COMPLETED"}},
             "timestamp": "2026-09-20T09:02:00"},
        ])
        assert detect_recovery(s) is None


class TestFullPipeline:
    def test_analyze_session_returns_result(self):
        s = make_session([
            {"role": "user", "content": "Refund status"},
            {"role": "tool", "content": "check",
             "tool_call": {"tool_name": "check_refund_status", "arguments": {"order_id": "ORD-1"},
                           "result": {"refund_status": "PENDING"}},
             "timestamp": "2026-09-20T09:01:00"},
            {"role": "assistant", "content": "Refund completed!"},
        ])
        result = analyze_session(s)
        assert result.session_id == "test"
        assert isinstance(result.classification, str)
        assert 0.0 <= result.overall_confidence <= 1.0
        assert result.processing_time_ms >= 0
        assert isinstance(result.findings, list)
        assert len(result.findings) > 0

    def test_analysis_has_required_fields(self):
        s = make_session([
            {"role": "user", "content": "Order ORD-1"},
            {"role": "tool", "content": "lookup",
             "tool_call": {"tool_name": "lookup_customer", "arguments": {"customer_id": "CUST-100"},
                           "result": {"customer_id": "CUST-999"}},
             "timestamp": "2026-09-20T09:01:00"},
        ])
        result = analyze_session(s)
        assert len(result.findings) > 0
        for f in result.findings:
            assert f.type
            assert f.classification
            assert 0.0 <= f.confidence <= 1.0
            assert f.reason
            assert f.evidence
            assert f.recommended_action

    def test_analyze_all_sessions(self):
        from agentlens.dataset.generator import generate_dataset
        from agentlens.models import Session
        data = generate_dataset()
        sessions = [Session(**s) for s in data]
        analyses, summary = analyze_all_sessions(sessions)
        assert len(analyses) == 48
        assert summary["total_sessions"] == 48
        assert "successful" in summary
        assert "recovered" in summary
        assert "likely_failures" in summary
        assert "ambiguous" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
