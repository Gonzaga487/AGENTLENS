import urllib.request, zipfile, io, os, subprocess, sys

url = "https://github.com/cloudflare/cloudflared/releases/download/2024.9.2/cloudflared-windows-amd64.zip"
print(f"Downloading cloudflared from {url}...")
try:
    r = urllib.request.urlopen(url, timeout=30)
    data = r.read()
    print(f"Downloaded {len(data)} bytes")
    
    z = zipfile.ZipFile(io.BytesIO(data))
    z.extractall(os.getcwd())
    print("Extracted to cloudflared.exe")
    
    # Start tunnel
    print("Starting Cloudflare tunnel on port 8000...")
    proc = subprocess.Popen(
        [os.path.join(os.getcwd(), 'cloudflared.exe'), 'tunnel', '--url', 'http://localhost:8000'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    print(f"Cloudflare tunnel started with PID {proc.pid}")
    print("Waiting for URL...")
    
    # Read output for a few seconds
    import time
    time.sleep(5)
    try:
        line = proc.stderr.readline().decode().strip()
        if line:
            print(f"Tunnel output: {line}")
    except:
        pass
    
    # Try to access the tunnel
    import time
    time.sleep(2)
    try:
        r = urllib.request.urlopen('http://localhost:8000/api/summary', timeout=3)
        print(f"Server still accessible: {r.status}")
    except:
        print("Server may have stopped")
        
except Exception as e:
    print(f"Error: {e}")
    print("\nAlternative: Deploy on Render.com")
    print("Steps:")
    print("1. Create GitHub repo: git init && git add . && git commit -m 'AGENTLENS v2'")
    print("2. Push: gh repo create agentlens --public && git push origin main")
    print("3. Go to render.com, connect repo, create Web Service")
    print("   Build: pip install -r agentlens/requirements.txt")
    print("   Start: python -m agentlens.main --host 0.0.0.0 --port 8000")
    print("4. Get free public URL!")
