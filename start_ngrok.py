from pyngrok import ngrok
import subprocess, sys, time, os

# Set ngrok auth token (free tier allows 40 connections/hour)
# Get from: https://dashboard.ngrok.com/signup
# For free tier, you can use without auth but limited

print("Starting ngrok tunnel...")
try:
    # Start ngrok on port 8000
    public_url = ngrok.connect(8000, pyngrok_config=ngrok.PyngrokConfig())
    print(f"\n{'='*60}")
    print(f"AGENTLENS is LIVE at: {public_url.url}")
    print(f"{'='*60}")
    print(f"\nAPI Endpoints:")
    print(f"  Summary: {public_url.url}/api/summary")
    print(f"  Sessions: {public_url.url}/api/sessions")
    print(f"  Issues: {public_url.url}/api/issues")
    print(f"  Dashboard: {public_url.url}/")
    print(f"\nPress Ctrl+C to stop.")
    
    # Keep ngrok running
    while True:
        time.sleep(1)
except Exception as e:
    print(f"ngrok error: {e}")
    print("\nTrying alternative: running ngrok CLI...")
    # Fallback: use ngrok CLI
    subprocess.Popen(['ngrok', 'http', '8000'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    print("Ngrok started. Check the ngrok dashboard for the URL.")
