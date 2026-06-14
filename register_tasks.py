import subprocess, os

DIR = os.path.dirname(os.path.abspath(__file__))

tasks = [
    ("GitHubTrendingDaily",   "DAILY",   None, "run_daily.bat"),
    ("GitHubTrendingWeekly",  "WEEKLY",  "MON", "run_weekly.bat"),
    ("GitHubTrendingMonthly", "MONTHLY", "1",   "run_monthly.bat"),
]

for name, sc, day, bat in tasks:
    tr = f'"{os.path.join(DIR, bat)}"'
    sc_day = f"/D {day}" if day else ""
    cmd = f'SCHTASKS /Create /TN "{name}" /TR {tr} /SC {sc} {sc_day} /ST 09:00 /F'
    print(f"[*] {name}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"    OK")
    else:
        print(f"    FAIL: {result.stderr.strip() or result.stdout.strip()}")
