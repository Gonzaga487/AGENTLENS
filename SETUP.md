# AGENTLENS - Setup & Run Instructions

## Prerequisites
- Python 3.10+
- pip (Python package manager)
- Internet connection (for first-time package installation)

## Installation (One-Time Setup)

### Method 1: Using the setup script (Recommended)
```cmd
cd C:\Users\User\Documents\AGENTLENS
python start.py
```

### Method 2: Manual
```cmd
cd C:\Users\User\Documents\AGENTLENS

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

## Running the Server
```cmd
cd C:\Users\User\Documents\AGENTLENS
python -m agentlens.main
```

Then open **http://localhost:8000** in your browser.

## Running Tests
```cmd
cd C:\Users\User\Documents\AGENTLENS
python -m pytest agentlens/tests/test_analysis.py -v
```

## Quick Verification
```cmd
# Check if server is running
curl http://localhost:8000/api/health

# Check all sessions
curl http://localhost:8000/api/sessions

# Check summary
curl http://localhost:8000/api/summary
```

## Architecture
```
Dataset (48 sessions) → Deterministic Checks → Classification → Grouping → Dashboard
```

## What Gets Detected
1. **Unsupported Success Claims** - Agent says "completed" but tool says PENDING
2. **Repeated Questions** - Agent asks for info user already provided
3. **No-Progress Searches** - Agent searches repeatedly with empty results
4. **Wrong Customer Record** - Retrieved record differs from requested
5. **Incomplete Requests** - Agent completes only part of multi-part request
6. **Ambiguous Cases** - Evidence insufficient → recommend human review

## Classifications
- **SUCCESSFUL** - Clean pass
- **RECOVERED** - Failed initially but recovered
- **LIKELY_FAILURE** - Evidence indicates failure
- **AMBIGUOUS** - Insufficient evidence → human review needed

## No LLM API Key Needed
Phase 1 uses deterministic checks only. AI cost is tracked when semantic analysis is triggered.
No API key is stored or required.
