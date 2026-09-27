# AGENTLENS Installation Guide

## Quick Start

### Option 1: Windows (run.bat)
```cmd
run.bat
```

### Option 2: Manual (any platform)
```bash
# 1. Navigate to project
cd AGENTLENS

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
python -m agentlens.main

# 5. Open browser to http://localhost:8000
```

### Option 3: Install as package
```bash
pip install -e .
agentlens
```

## Running Tests

```bash
pip install pytest
python -m pytest agentlens/tests/test_analysis.py -v
```

## Project Structure

```
AGENTLENS/
├── agentlens/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── requirements.txt
│   ├── models/
│   │   ├── __init__.py      # Pydantic models (Session, Finding, etc.)
│   ├── analysis/
│   │   ├── __init__.py
│   │   └── engine.py        # Analysis engine + classification
│   ├── api/
│   │   ├── __init__.py
│   │   ├── health.py        # GET /api/health
│   │   ├── sessions.py      # GET /api/sessions, /api/sessions/{id}
│   │   └── summary.py       # GET /api/summary, /api/issues, /api/metrics
│   ├── dataset/
│   │   ├── __init__.py
│   │   └── generator.py     # 48 synthetic sessions
│   ├── services/
│   │   └── __init__.py
│   ├── static/
│   │   ├── index.html       # Dashboard UI
│   │   ├── css/style.css    # Dark/light theme styles
│   │   └── js/app.js        # Frontend logic
│   └── tests/
│       └── test_analysis.py # Full test suite
├── requirements.txt
├── setup.py
├── .env.example
├── README.md
├── INSTALL.md
└── run.bat
```

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Health check |
| `/api/sessions` | GET | List all sessions |
| `/api/sessions/{id}` | GET | Get specific session |
| `/api/sessions/{id}/analysis` | GET | Analysis results |
| `/api/summary` | GET | Overview summary |
| `/api/issues` | GET | Grouped issues |
| `/api/metrics` | GET | Processing metrics |

## Features

- ✅ 48 synthetic agent sessions (8 types)
- ✅ Deterministic failure detection (no LLM needed)
- ✅ 6 failure categories
- ✅ 4 classifications: SUCCESSFUL, RECOVERED, LIKELY_FAILURE, AMBIGUOUS
- ✅ Evidence highlighting
- ✅ Recovery vs failure distinction
- ✅ Issue grouping and ranking
- ✅ Dark/light theme dashboard
- ✅ Chart.js visualizations
- ✅ Clickable issue groups
- ✅ Full test suite
- ✅ Processing metrics

## Architecture

```
Dataset → Deterministic Checks → Classification → Grouping → Dashboard
```

No LLM API calls needed for Phase 1. AI cost is tracked when semantic analysis is triggered for ambiguous cases.
