"""AGENTLENS Startup Script.

Usage:
    python start.py
    # Then open http://localhost:8000 in your browser
"""
import sys
import subprocess

def check_and_install():
    """Check if dependencies are available, install if needed."""
    packages = ["fastapi", "pydantic", "uvicorn", "sklearn", "pandas", "jinja2", "httpx", "multipart"]
    missing = []
    for pkg in packages:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            missing.append(pkg)
    return missing

def main():
    missing = check_and_install()
    if missing:
        print(f"Installing missing packages: {', '.join(missing)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    print("Starting AGENTLENS server...")
    print("Open http://localhost:8000 in your browser")
    print("Press Ctrl+C to stop\n")

    import uvicorn
    uvicorn.run("agentlens.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
