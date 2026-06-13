import subprocess, sys, os

DIR = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable  # 使用完整 Python 路径，避免定时任务找不到

tasks = [
    ("GitHubTrendingDaily",  "DAILY",         None, "daily"),
    ("GitHubTrendingWeekly", "WEEKLY",        "MON", "weekly"),
]

for name, sc, day, arg in tasks:
    tr = f'"{PY}" "{DIR}\\main.py" {arg}'
    sc_day = f"/D {day}" if day else ""
    cmd = f'SCHTASKS /Create /TN "{name}" /TR {tr} /SC {sc} {sc_day} /ST 09:00 /F'
    print(f"[*] {name}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"    OK")
    else:
        print(f"    FAIL: {result.stderr.strip() or result.stdout.strip()}")
