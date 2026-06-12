import subprocess, sys

DIR = r"C:\Users\steve\Desktop\抓取提交"

tasks = [
    ("GitHubTrendingDaily",  "DAILY",         "daily"),
    ("GitHubTrendingWeekly", "WEEKLY", "MON",  "weekly"),
]

for name, *rest in tasks:
    if len(rest) == 2:
        sc, arg = rest
        cmd = f'SCHTASKS /Create /TN "{name}" /TR "python {DIR}\\main.py {arg}" /SC {sc} /ST 09:00 /F'
    else:
        sc, day, arg = rest
        cmd = f'SCHTASKS /Create /TN "{name}" /TR "python {DIR}\\main.py {arg}" /SC {sc} /D {day} /ST 09:00 /F'
    print(f"[*] {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"    OK")
    else:
        print(f"    FAIL: {result.stderr.strip() or result.stdout.strip()}")
