import sys
import traceback

from trending.fetcher import fetch_trending
from trending.models import Report
from config import get_summarizer, get_notifiers


def _fix_windows_encoding():
    """修复 Windows 终端 GBK 编码问题"""
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def run(period: str) -> Report:
    """执行一次报告生成与推送。period: 'daily' | 'weekly'"""
    print(f"[*] 开始抓取 GitHub Trending ({period}) ...")
    repos = fetch_trending(period)
    print(f"    获取到 {len(repos)} 个仓库")

    report = Report(period=period, repos=repos)

    # 摘要
    summarizer = get_summarizer()
    if summarizer:
        print(f"[*] 使用 {type(summarizer).__name__} 生成 AI 摘要 ...")
        try:
            report.content = summarizer.summarize(repos, period)
        except Exception:
            print(f"    AI 摘要失败，使用纯列表格式")
            traceback.print_exc()
            report.content = _fallback_report(repos, period)
    else:
        print("[*] 未配置 AI API key，使用纯列表格式")
        report.content = _fallback_report(repos, period)

    # 保存到本地
    filepath = report.save()
    print(f"[*] 报告已保存: {filepath}")

    # 推送
    notifiers = get_notifiers()
    if notifiers:
        print(f"[*] 推送至 {len(notifiers)} 个通道 ...")
        for n in notifiers:
            name = type(n).__name__
            ok = n.send(report.title, report.content)
            status = "OK" if ok else "FAIL"
            print(f"    {name}: {status}")
    else:
        print("[*] 未配置推送通道，仅本地保存")

    return report


def _fallback_report(repos, period: str) -> str:
    label = "今日" if period == "daily" else "本周"
    lines = [f"# GitHub Trending {label}报告\n"]
    for i, r in enumerate(repos, 1):
        lines.append(
            f"{i}. **[{r.full_name}]({r.url})** ⭐{r.total_stars} (+{r.stars_period})"
            f" | {r.language or '未知'}"
            f"\n   > {r.description or '(无描述)'}\n"
        )
    return "\n".join(lines)


def main():
    _fix_windows_encoding()
    if len(sys.argv) < 2 or sys.argv[1] not in ("daily", "weekly"):
        print("用法: python main.py [daily|weekly]")
        print("  daily  - 生成每日 GitHub Trending 报告")
        print("  weekly - 生成每周 GitHub Trending 报告")
        sys.exit(1)

    period = sys.argv[1]
    try:
        run(period)
        print("\n[Done]")
    except Exception:
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
