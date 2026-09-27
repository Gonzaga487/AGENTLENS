import shutil, os

dirs = [
    r'C:\Users\User\Documents\AGENTLENS\agentlens\analysis\__pycache__',
    r'C:\Users\User\Documents\AGENTLENS\agentlens\models\__pycache__',
    r'C:\Users\User\Documents\AGENTLENS\agentlens\api\__pycache__',
    r'C:\Users\User\Documents\AGENTLENS\agentlens\dataset\__pycache__',
    r'C:\Users\User\Documents\AGENTLENS\agentlens\__pycache__',
]

for d in dirs:
    if os.path.exists(d):
        shutil.rmtree(d)
        print(f"Cleared: {d}")
    else:
        print(f"Not found: {d}")

print("Cache cleared!")
