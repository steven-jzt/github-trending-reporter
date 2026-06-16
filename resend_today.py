"""补发今日已生成的报告——给新增收件人用"""
import sys
from datetime import datetime
from pathlib import Path
from config import get_notifiers

REPORTS_DIR = Path(__file__).parent / "reports"
TODAY = datetime.now().strftime("%Y-%m-%d")


def main():
    files = sorted(REPORTS_DIR.glob(f"github-trending-*-{TODAY}.md"))
    if not files:
        print(f"[*] 今天 ({TODAY}) 没有已生成的报告")
        sys.exit(0)

    notifiers = get_notifiers()
    if not notifiers:
        print("[*] 未配置推送通道")
        sys.exit(0)

    print(f"[*] 找到 {len(files)} 份今日报告，收件人 {len(notifiers)} 个通道")

    for f in files:
        content = f.read_text(encoding="utf-8")
        period = f.stem.split("-")[2]
        label = {"daily": "每日", "weekly": "每周", "monthly": "月度"}.get(period, period)
        title = f"GitHub Trending {label}报告 ({TODAY})"

        print(f"    发送: {f.name}")
        for n in notifiers:
            name = type(n).__name__
            ok = n.send(title, content)
            status = "OK" if ok else "FAIL"
            print(f"      {name}: {status}")

    print("[Done]")


if __name__ == "__main__":
    main()
