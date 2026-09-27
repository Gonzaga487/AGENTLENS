import subprocess, os, signal, time, socket

# Find PIDs listening on port 8000
r = subprocess.run(['netstat', '-ano', '-p', 'tcp'], capture_output=True, text=True)
lines = r.stdout.split('\n')
pids = set()
for line in lines:
    if ':8000' in line and 'LISTENING' in line:
        parts = line.strip().split()
        if parts:
            try:
                pid = int(parts[-1])
                if pid > 0:
                    pids.add(pid)
            except:
                pass

print(f"Found PIDs on port 8000: {pids}")
for pid in pids:
    try:
        os.kill(pid, signal.CTRL_C_EVENT)
        print(f"Killed PID {pid}")
    except Exception as e:
        print(f"Could not kill PID {pid}: {e}")

time.sleep(2)

# Verify port is closed
s = socket.socket()
result = s.connect_ex(('127.0.0.1', 8000))
s.close()
print('Port 8000 is', 'open' if result == 0 else 'closed')
