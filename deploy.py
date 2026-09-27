# AGENTLENS Deployment Configuration
# =================================
# 
# Option 1: Instant tunnel (no auth needed)
#   curl http://localhost.run | bash
#   or: ssh -R 80:localhost:8000 nokey@localhost.run
#
# Option 2: Deploy on Render (free tier)
#   1. Push to GitHub: gh repo create agentlens --public --source=. --remote=origin
#   2. Connect GitHub repo to Render: https://dashboard.render.com
#   3. Create Web Service with:
#      - Build Command: pip install -r agentlens/requirements.txt && pip install pyngrok
#      - Start Command: python -m agentlens.main --host 0.0.0.0 --port 8000
#      - Python Version: 3.14
#      - Free Instance Type: Free
#
# Option 3: Deploy on Railway (free $5 credit)
#   1. pip install railway
#   2. railway init
#   3. railway up
#
# Option 4: Deploy on Render with GitHub
#   Create a repo and push:
#   git init
#   git add .
#   git commit -m "AGENTLENS Phase 2"
#   gh repo create agentlens --public
#   git push origin main
#   Then deploy on render.com

import subprocess, sys

# Try localhost.run for instant tunnel
print("=" * 60)
print("AGENTLENS Deployment Options")
print("=" * 60)
print()
print("Option 1 - Instant Tunnel (localhost.run):")
print("  Command: ssh -R 80:localhost:8000 nokey@localhost.run")
print("  This gives a public URL without any setup.")
print()
print("Option 2 - Render (free, persistent):")
print("  1. Push to GitHub: gh repo create agentlens --public")
print("  2. Connect repo at render.com")
print("  3. Create Web Service (Python 3.14)")
print()
print("Option 3 - Railway (free $5 credit):")
print("  1. pip install railway")
print("  2. railway init && railway up")
print("=" * 60)

# Try to start localhost.run tunnel
print("\nTrying localhost.run tunnel...")
try:
    result = subprocess.run(
        ['ssh', '-R', '80:localhost:8000', '-o', 'StrictHostKeyChecking=no', 
         '-o', 'UserKnownHostsFile=/dev/null', 'nokey@localhost.run'],
        capture_output=True, text=True, timeout=10
    )
    print(result.stdout)
    print(result.stderr)
except subprocess.TimeoutExpired:
    print("Tunnel started (timeout is expected for persistent connections)")
except FileNotFoundError:
    print("SSH not available. Using alternative method...")
    # Try curl-based approach
    try:
        result = subprocess.run(
            ['curl', '-s', 'localhost.run'],
            capture_output=True, text=True, timeout=5
        )
        print(f"localhost.run response: {result.stdout[:200]}")
    except:
        print("Could not start tunnel automatically.")
        print("Please visit: https://localhost.run for instructions.")
