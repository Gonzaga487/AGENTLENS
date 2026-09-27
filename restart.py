import subprocess, sys, os

# Kill any running Python processes on port 8000
result = subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
print("Old process killed")

# Wait a moment
import time
time.sleep(2)

# Start the server
print("Starting server...")
proc = subprocess.Popen([sys.executable, '-m', 'agentlens.main'],
                        cwd=r'C:\Users\User\Documents\AGENTLENS',
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True)

# Wait for startup
time.sleep(3)

# Test the API
import urllib.request
try:
    with urllib.request.urlopen('http://localhost:8000/api/summary') as response:
        data = response.read().decode('utf-8')
        import json
        summary = json.loads(data)
        print(f"Recovered count: {summary['recovered']}")
        print(f"Successful count: {summary['successful']}")
except Exception as e:
    print(f"Error: {e}")

# Keep running
proc.wait()
