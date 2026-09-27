import sys
sys.path.insert(0, r'C:\Users\User\Documents\AGENTLENS')

# Force reimport
import importlib
if 'agentlens.analysis.engine' in sys.modules:
    del sys.modules['agentlens.analysis.engine']
if 'agentlens.models' in sys.modules:
    del sys.modules['agentlens.models']

from agentlens.analysis.engine import classify_session, analyze_session
from agentlens.models import Session, Message, ToolCall

# Create a recovered session
msgs = [
    Message(role='user', content='Find order ORD-5', timestamp='2026-09-20T09:00:00'),
    Message(role='tool', content='search', timestamp='2026-09-20T09:01:00',
            tool_call=ToolCall(tool_name='search_orders', arguments={'query': 'ORD-5'},
                               result={'results': [], 'total': 0}, timestamp='2026-09-20T09:01:00')),
    Message(role='tool', content='lookup', timestamp='2026-09-20T09:02:00',
            tool_call=ToolCall(tool_name='lookup_order', arguments={'order_id': 'ORD-5'},
                               result={'order_id': 'ORD-5', 'status': 'delivered'}, timestamp='2026-09-20T09:02:00')),
]
s = Session(id='test-recovered', title='Test', created_at='2026-09-20T09:00:00', messages=msgs)
cls, conf = classify_session(s, [])
print(f"Classification: {cls}, Confidence: {conf}")
assert cls == "RECOVERED", f"Expected RECOVERED, got {cls}"
print("✅ Fix verified!")

# Now test analyze_session
result = analyze_session(s)
print(f"Analysis classification: {result.classification}")
assert result.classification == "RECOVERED", f"Expected RECOVERED, got {result.classification}"
print("✅ analyze_session fix verified!")
