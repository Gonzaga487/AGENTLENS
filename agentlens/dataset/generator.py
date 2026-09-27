"""Generate synthetic agent conversation sessions for AGENTLENS."""
from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta
from typing import Optional


def _ts(offset_minutes: int = 0) -> str:
    base = datetime(2026, 9, 20, 9, 0, 0)
    return (base + timedelta(minutes=offset_minutes)).isoformat()


def _make_tool_call(tool_name: str, args: dict, result: dict, ts_offset: int) -> dict:
    return {
        "role": "tool",
        "content": f"Tool call: {tool_name}({args})",
        "timestamp": _ts(ts_offset),
        "tool_call": {
            "tool_name": tool_name,
            "arguments": args,
            "result": result,
            "timestamp": _ts(ts_offset),
        },
    }


# ───────────────────────────────────────────────────────────────────────────────
# Session factories
# ───────────────────────────────────────────────────────────────────────────────

def success_session(idx: int) -> dict:
    """Clean session: agent resolves request correctly in one go."""
    cid = f"CUST-{random.randint(1000,9999)}"
    oid = f"ORD-{random.randint(1000,9999)}"
    return {
        "id": f"sess-success-{idx:03d}",
        "title": f"Refund processing for {cid}",
        "customer_id": cid,
        "order_id": oid,
        "created_at": _ts(idx * 10),
        "status": "completed",
        "messages": [
            {"role": "user", "content": f"I need to refund order {oid} for {cid}. The item was damaged.", "timestamp": _ts(idx*10)},
            {"role": "assistant", "content": "Let me look up your order.", "timestamp": _ts(idx*10+1)},
            _make_tool_call("lookup_order", {"order_id": oid}, {"order_id": oid, "status": "delivered", "customer_id": cid, "items": ["widget"]}, idx*10+2),
            {"role": "assistant", "content": "I found your order. It's delivered. Initiating refund now.", "timestamp": _ts(idx*10+3)},
            _make_tool_call("process_refund", {"order_id": oid, "customer_id": cid}, {"refund_id": f"REF-{idx}", "status": "COMPLETED", "amount": 49.99}, idx*10+4),
            {"role": "assistant", "content": f"Refund of $49.99 has been completed for order {oid}. Your refund ID is REF-{idx}.", "timestamp": _ts(idx*10+5)},
        ],
    }


def recovered_session(idx: int) -> dict:
    """Agent fails initially but recovers: searches → no result → finds customer → completes."""
    cid = f"CUST-{random.randint(1000,9999)}"
    oid = f"ORD-{random.randint(1000,9999)}"
    return {
        "id": f"sess-recovered-{idx:03d}",
        "title": f"Order lookup - recovered for {cid}",
        "customer_id": cid,
        "order_id": oid,
        "created_at": _ts(idx * 10 + 5),
        "status": "completed",
        "messages": [
            {"role": "user", "content": f"Can you find my order {oid}? I think the order number is {oid}.", "timestamp": _ts(idx*10)},
            {"role": "assistant", "content": "Let me search for that order.", "timestamp": _ts(idx*10+1)},
            _make_tool_call("search_orders", {"query": oid}, {"results": [], "message": "No orders found."}, idx*10+2),
            {"role": "assistant", "content": "Hmm, nothing there. Let me try a broader search.", "timestamp": _ts(idx*10+3)},
            _make_tool_call("search_orders", {"query": oid}, {"results": [], "message": "No orders found."}, idx*10+4),
            {"role": "assistant", "content": "Let me look up by customer instead.", "timestamp": _ts(idx*10+5)},
            _make_tool_call("lookup_customer", {"customer_id": cid}, {"customer_id": cid, "name": "Jane Doe", "orders": [oid]}, idx*10+6),
            {"role": "assistant", "content": f"Found it! Your order {oid} is on file. Let me check its status.", "timestamp": _ts(idx*10+7)},
            _make_tool_call("lookup_order", {"order_id": oid}, {"order_id": oid, "status": "shipped", "customer_id": cid}, idx*10+8),
            {"role": "assistant", "content": f"Order {oid} is shipped and confirmed for {cid}. Everything looks good!", "timestamp": _ts(idx*10+9)},
        ],
    }


def unsupported_success_claim(idx: int) -> dict:
    """Agent says 'refund completed' but tool says PENDING."""
    cid = f"CUST-{random.randint(1000,9999)}"
    oid = f"ORD-{random.randint(1000,9999)}"
    return {
        "id": f"sess-failure-claim-{idx:03d}",
        "title": f"False success claim for {cid}",
        "customer_id": cid,
        "order_id": oid,
        "created_at": _ts(idx * 10 + 10),
        "status": "completed",
        "messages": [
            {"role": "user", "content": f"Status of my refund for {oid}?", "timestamp": _ts(idx*10)},
            {"role": "assistant", "content": "Let me check.", "timestamp": _ts(idx*10+1)},
            _make_tool_call("check_refund_status", {"order_id": oid}, {"refund_id": f"REF-{idx}", "refund_status": "PENDING", "amount": 29.99}, idx*10+2),
            {"role": "assistant", "content": f"Your refund of $29.99 has been completed! You should see it soon.", "timestamp": _ts(idx*10+3)},
        ],
    }


def repeated_questions(idx: int) -> dict:
    """Agent asks for the same information multiple times."""
    cid = f"CUST-{random.randint(1000,9999)}"
    oid = f"ORD-{random.randint(1000,9999)}"
    return {
        "id": f"sess-failure-repeat-{idx:03d}",
        "title": f"Repeated questions for {cid}",
        "customer_id": cid,
        "order_id": oid,
        "created_at": _ts(idx * 10 + 20),
        "status": "completed",
        "messages": [
            {"role": "user", "content": f"My order is {oid} for {cid}. I need help.", "timestamp": _ts(idx*10)},
            {"role": "assistant", "content": "I can help! What is your order number?", "timestamp": _ts(idx*10+1)},
            {"role": "user", "content": f"My order is {oid}.", "timestamp": _ts(idx*10+2)},
            {"role": "assistant", "content": "Thanks! What is your customer ID?", "timestamp": _ts(idx*10+3)},
            {"role": "user", "content": f"My customer ID is {cid}.", "timestamp": _ts(idx*10+4)},
            {"role": "assistant", "content": "Great! Can you tell me your order number again?", "timestamp": _ts(idx*10+5)},
            {"role": "user", "content": f"It's {oid}, I already told you.", "timestamp": _ts(idx*10+6)},
            {"role": "assistant", "content": "Sorry! And your customer ID please?", "timestamp": _ts(idx*10+7)},
            {"role": "user", "content": f"{cid}.", "timestamp": _ts(idx*10+8)},
            {"role": "assistant", "content": "Perfect, now let me look it up.", "timestamp": _ts(idx*10+9)},
            _make_tool_call("lookup_order", {"order_id": oid}, {"order_id": oid, "customer_id": cid}, idx*10+10),
        ],
    }


def no_progress_search(idx: int) -> dict:
    """Agent searches repeatedly without gaining new information."""
    cid = f"CUST-{random.randint(1000,9999)}"
    return {
        "id": f"sess-failure-search-{idx:03d}",
        "title": f"No-progress searches for {cid}",
        "customer_id": cid,
        "created_at": _ts(idx * 10 + 30),
        "status": "completed",
        "messages": [
            {"role": "user", "content": f"Can you help me with order issues for {cid}?", "timestamp": _ts(idx*10)},
            {"role": "assistant", "content": "Let me search.", "timestamp": _ts(idx*10+1)},
            _make_tool_call("search", {"query": "order issue"}, {"results": [], "total": 0}, idx*10+2),
            {"role": "assistant", "content": "Let me search again.", "timestamp": _ts(idx*10+3)},
            _make_tool_call("search", {"query": "order issue"}, {"results": [], "total": 0}, idx*10+4),
            {"role": "assistant", "content": "One more search.", "timestamp": _ts(idx*10+5)},
            _make_tool_call("search", {"query": "order issue"}, {"results": [], "total": 0}, idx*10+6),
            {"role": "assistant", "content": "I'm having trouble finding anything.", "timestamp": _ts(idx*10+7)},
            _make_tool_call("search", {"query": "order issue"}, {"results": [], "total": 0}, idx*10+8),
            {"role": "assistant", "content": "Let me try one more search.", "timestamp": _ts(idx*10+9)},
            _make_tool_call("search", {"query": "order issue"}, {"results": [], "total": 0}, idx*10+10),
        ],
    }


def wrong_customer_record(idx: int) -> dict:
    """Agent retrieves a different customer's record than the one requested."""
    cid = f"CUST-{random.randint(1000,9999)}"
    wrong_cid = f"CUST-{random.randint(1000,9999)}"
    oid = f"ORD-{random.randint(1000,9999)}"
    return {
        "id": f"sess-failure-wrong-cust-{idx:03d}",
        "title": f"Wrong customer record for {cid}",
        "customer_id": cid,
        "order_id": oid,
        "created_at": _ts(idx * 10 + 40),
        "status": "completed",
        "messages": [
            {"role": "user", "content": f"I'm {cid}. Can you check my order {oid}?", "timestamp": _ts(idx*10)},
            {"role": "assistant", "content": "Looking up your account.", "timestamp": _ts(idx*10+1)},
            _make_tool_call("lookup_customer", {"customer_id": cid}, {"customer_id": wrong_cid, "name": "Wrong Person", "email": "wrong@example.com"}, idx*10+2),
            {"role": "assistant", "content": f"Hi! I see your account for {wrong_cid}. What can I help with?", "timestamp": _ts(idx*10+3)},
        ],
    }


def incomplete_request(idx: int) -> dict:
    """Agent completes only part of the request but claims everything is done."""
    cid = f"CUST-{random.randint(1000,9999)}"
    oid = f"ORD-{random.randint(1000,9999)}"
    return {
        "id": f"sess-failure-incomplete-{idx:03d}",
        "title": f"Incomplete request for {cid}",
        "customer_id": cid,
        "order_id": oid,
        "created_at": _ts(idx * 10 + 50),
        "status": "completed",
        "messages": [
            {"role": "user", "content": f"Cancel order {oid} AND refund my payment for {cid}.", "timestamp": _ts(idx*10)},
            {"role": "assistant", "content": "Let me handle that.", "timestamp": _ts(idx*10+1)},
            _make_tool_call("cancel_order", {"order_id": oid}, {"order_id": oid, "status": "CANCELLED"}, idx*10+2),
            {"role": "assistant", "content": f"Done! Your order {oid} has been fully processed and refunded.", "timestamp": _ts(idx*10+3)},
        ],
    }


def ambiguous_session(idx: int) -> dict:
    """Evidence is insufficient to classify definitively."""
    cid = f"CUST-{random.randint(1000,9999)}"
    oid = f"ORD-{random.randint(1000,9999)}"
    return {
        "id": f"sess-ambiguous-{idx:03d}",
        "title": f"Ambiguous case for {cid}",
        "customer_id": cid,
        "order_id": oid,
        "created_at": _ts(idx * 10 + 60),
        "status": "escalated",
        "messages": [
            {"role": "user", "content": f"Can you check if {oid} was delivered to {cid}?", "timestamp": _ts(idx*10)},
            {"role": "assistant", "content": "Checking...", "timestamp": _ts(idx*10+1)},
            _make_tool_call("lookup_order", {"order_id": oid}, {"order_id": oid, "status": "in_transit", "estimated_delivery": "2026-09-25"}, idx*10+2),
            {"role": "assistant", "content": f"Your order is in transit and expected by Sept 25.", "timestamp": _ts(idx*10+3)},
        ],
    }


# ───────────────────────────────────────────────────────────────────────────────
# Master generator
# ───────────────────────────────────────────────────────────────────────────────

def generate_dataset() -> list[dict]:
    sessions = []
    for i in range(8):
        sessions.append(success_session(i))
    for i in range(5):
        sessions.append(recovered_session(i))
    for i in range(8):
        sessions.append(unsupported_success_claim(i))
    for i in range(6):
        sessions.append(repeated_questions(i))
    for i in range(5):
        sessions.append(no_progress_search(i))
    for i in range(6):
        sessions.append(wrong_customer_record(i))
    for i in range(5):
        sessions.append(incomplete_request(i))
    for i in range(5):
        sessions.append(ambiguous_session(i))
    return sessions


if __name__ == "__main__":
    data = generate_dataset()
    print(f"Generated {len(data)} sessions")
