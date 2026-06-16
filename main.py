import sys
import traceback

from trending.fetcher import fetch_trending
from trending.models import Report
from config import get_summarizer, get_notifiers
from validate import run_preflight
from log import get_logger


def _fix_windows_encoding():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def run(period: str) -> Report:
    log = get_logger("main")
    log.info(f"开始抓取 GitHub Trending ({period}) ...")
    repos = fetch_trending(period)
    log.info(f"获取到 {len(repos)} 个仓库")

    report = Report(period=period, repos=repos)
    list_section = _list_report(repos, period)

    summarizer = get_summarizer()
    if summarizer:
        log.info(f"使用 {type(summarizer).__name__} 生成 AI 摘要 ...")
        try:
            ai_summary = summarizer.summarize(repos, period)
            report.content = ai_summary + "\n\n---\n\n## 本期全部项目列表\n\n" + list_section
        except Exception:
            log.warn("AI 摘要失败，降级为纯项目列表")
            log.error(traceback.format_exc())
            labels = {"daily": "今日", "weekly": "本周", "monthly": "本月"}
            label = labels.get(period, "本周")
            report.content = f"# GitHub Trending {label}报告\n\n" + list_section
    else:
        log.warn("未配置 AI API key，仅使用项目列表")
        labels = {"daily": "今日", "weekly": "本周", "monthly": "本月"}
        label = labels.get(period, "本周")
        report.content = f"# GitHub Trending {label}报告\n\n" + list_section

    filepath = report.save()
    log.info(f"报告已保存: {filepath}")

    notifiers = get_notifiers()
    if notifiers:
        log.info(f"推送至 {len(notifiers)} 个通道 ...")
        for n in notifiers:
            name = type(n).__name__
            ok = n.send(report.title, report.content)
            if ok:
                log.ok(f"{name}: 发送成功")
            else:
                log.error(f"{name}: 发送失败")
    else:
        log.warn("未配置推送通道，仅本地保存")

    return report


def _list_report(repos, period: str) -> str:
    lines: list[str] = []
    for i, r in enumerate(repos, 1):
        lines.append(
            f"{i}. **[{r.full_name}]({r.url})** ⭐{r.total_stars} (+{r.stars_period})"
            f" | {r.language or '未知'}"
            f"\n   > {r.description or '(无描述)'}\n"
        )
    return "\n".join(lines)


def main():
    _fix_windows_encoding()

    if len(sys.argv) < 2 or sys.argv[1] not in ("daily", "weekly", "monthly"):
        print("用法: python main.py [daily|weekly|monthly]")
        print("  daily   - 每日 GitHub Trending 报告")
        print("  weekly  - 每周 GitHub Trending 报告")
        print("  monthly - 月度 GitHub Trending 报告")
        sys.exit(1)

    period = sys.argv[1]
    log = get_logger("main")

    # 预检
    if not run_preflight():
        log.warn("预检发现问题，但继续尝试运行...")

    # 执行
    try:
        run(period)
        log.info("完成")
    except Exception:
        log.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
