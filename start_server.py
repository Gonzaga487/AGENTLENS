import subprocess, sys, time

# Start the server
proc = subprocess.Popen([sys.executable, '-m', 'agentlens.main', '--host', '0.0.0.0', '--port', '8000'], 
                       cwd='C:\\Users\\User\\Documents\\AGENTLENS',
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"Server started with PID {proc.pid}")
time.sleep(3)

# Verify it's running
import urllib.request
try:
    r = urllib.request.urlopen('http://127.0.0.1:8000/api/summary')
    print(f"Server is running! Status: {r.status}")
except Exception as e:
    print(f"Server not responding: {e}")
