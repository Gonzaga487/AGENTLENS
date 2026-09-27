# AGENTLENS - Complete Project Guide

## 🚀 Quick Start (After Dependencies Installed)

```cmd
cd C:\Users\User\Documents\AGENTLENS
python -m agentlens.main
```

Then open **http://localhost:8000** in your browser.

---

## 📁 Complete Project Structure

```
AGENTLENS/
├── agentlens/
│   ├── __init__.py              # Package init (version = "1.0.0")
│   ├── main.py                  # FastAPI app entry point
│   ├── requirements.txt         # Dependencies (fastapi, pydantic, uvicorn, jinja2, pytest)
│   ├── models/
│   │   ├── __init__.py          # Pydantic models: Session, Message, ToolCall, Finding, Evidence,
│   │   │                        # AnalysisResult, Summary, IssueGroup, Metrics
│   ├── analysis/
│   │   ├── __init__.py
│   │   └── engine.py            # Analysis engine: deterministic checks + classification + grouping
│   ├── api/
│   │   ├── __init__.py
│   │   ├── health.py            # GET /api/health
│   │   ├── sessions.py          # GET /api/sessions, /api/sessions/{id}, /api/sessions/{id}/analysis
│   │   └── summary.py           # GET /api/summary, /api/issues, /api/metrics
│   ├── dataset/
│   │   ├── __init__.py
│   │   └── generator.py         # 48 synthetic sessions (8 types)
│   ├── services/
│   │   └── __init__.py
│   ├── static/
│   │   ├── index.html           # Dashboard HTML (dark/light theme)
│   │   ├── css/
│   │   │   └── style.css        # Complete dark/light theme styles
│   │   └── js/
│   │       └── app.js           # Frontend: dashboard, sessions, issues, session detail
│   ├── tests/
│   │   └── test_analysis.py     # Full test suite (9 test classes)
│   └── templates/               # Empty (reserved for future use)
├── requirements.txt             # Root requirements
├── setup.py                     # Package setup
├── start.py                     # Startup script with auto-install
├── run.bat                      # Windows batch script
├── .env.example                 # Environment template
├── README.md                    # Project overview
├── INSTALL.md                   # Installation guide
├── SETUP.md                     # Setup instructions
└── setup_dirs.py                # Directory creation script
```

---

## 📦 Installation (After Network is Available)

```cmd
cd C:\Users\User\Documents\AGENTLENS

# Install dependencies
pip install -r requirements.txt

# Or use the startup script
python start.py

# Run the server
python -m agentlens.main
```

## 🧪 Run Tests

```cmd
cd C:\Users\User\Documents\AGENTLENS
python -m pytest agentlens/tests/test_analysis.py -v
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/sessions` | List all sessions (limit, offset params) |
| GET | `/api/sessions/{id}` | Get specific session |
| GET | `/api/sessions/{id}/analysis` | Analysis results |
| GET | `/api/summary` | Overview summary |
| GET | `/api/issues` | Grouped issues by severity |
| GET | `/api/metrics` | Processing metrics |
| GET | `/` | Dashboard (HTML) |

---

## 🎯 Features

### Failure Detection (6 Categories)
1. **Unsupported Success Claims** - Agent says "completed" but tool says PENDING
2. **Repeated Questions** - Agent asks for info the user already provided
3. **No-Progress Searches** - Agent searches repeatedly with empty results
4. **Wrong Customer Record** - Retrieved record differs from requested
5. **Incomplete Requests** - Agent completes only part of multi-part request
6. **Ambiguous Cases** - Evidence insufficient → recommend human review

### Classification System
- **SUCCESSFUL** - Clean pass, no issues
- **RECOVERED** - Failed initially but recovered
- **LIKELY_FAILURE** - Evidence indicates failure
- **AMBIGUOUS** - Insufficient evidence → human review needed

### Dashboard Features
- Animated stat counters (Sessions, Successful, Recovered, Likely Failures, Ambiguous)
- Doughnut chart: classification distribution
- Horizontal bar chart: issues by type/severity
- Clickable issue groups (drill-down modal)
- Session table with search/filter
- Session detail view with chronological conversation
- Evidence highlighting on findings
- Processing metrics (time, events, AI cost, throughput)
- Dark/light theme toggle

---

## 🏗️ Architecture

```
Dataset (48 synthetic sessions)
    ↓
Deterministic checks (first)
    ↓
AI semantic analysis (when needed)
    ↓
Classification + confidence
    ↓
Group similar issues
    ↓
Investigation priority
    ↓
Dashboard (charts + clickable groups)
```

**Design Principle**: Deterministic checks first, AI only where semantic reasoning is necessary.

---

## 📊 Dataset

48 synthetic sessions:
- 8 Successful
- 5 Recovered
- 8 Unsupported Success Claims
- 6 Repeated Questions
- 5 No-Progress Searches
- 6 Wrong Customer Records
- 5 Incomplete Requests
- 5 Ambiguous Cases

Each session has: user messages, assistant messages, tool calls, tool results, timestamps, customer/order IDs.

---

## 🧠 Analysis Engine

The `analysis/engine.py` implements:
- `_find_unsupported_success_claim()` - Detects false completion claims
- `_find_repeated_questions()` - Detects redundant questions
- `_find_no_progress_searches()` - Detects unproductive searches
- `_find_wrong_customer_record()` - Detects wrong customer lookups
- `_find_incomplete_request()` - Detects partial completions
- `classify_session()` - Determines final classification
- `group_issues()` - Groups and ranks findings by severity
- `analyze_all_sessions()` - Batch analysis pipeline

---

## 🎨 Frontend

The `static/` directory contains:
- `index.html` - Dashboard with sidebar navigation, stats cards, charts, session table
- `css/style.css` - Dark theme (default) / light theme toggle, cards, badges, responsive design
- `js/app.js` - Frontend logic: data loading, navigation, charts (Chart.js), session detail view

---

## ✅ Testing

9 test classes covering:
- TestUnsupportedSuccessClaim (2 tests)
- TestRepeatedQuestions (2 tests)
- TestNoProgressSearches (2 tests)
- TestWrongCustomerRecord (2 tests)
- TestIncompleteRequest (2 tests)
- TestRecovery (2 tests)
- TestAmbiguousCases (1 test)
- TestFullPipeline (3 tests)
- TestDataset (3 tests)

---

## 🚫 Not in Phase 1
- Authentication / payments
- Microservices / live ingestion
- Automatic fixes
- Real LLM API calls (no API key needed)
- Unnecessary features

---

## 💡 No API Key Required

Phase 1 uses deterministic checks only. AI cost is tracked when semantic analysis is triggered for ambiguous cases. No API key is stored or required.

---

**Built for the SupplyzPro "Find the Hidden Failures" Hackathon Challenge.**
