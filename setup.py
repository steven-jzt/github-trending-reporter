"""交互式配置向导 —— 一键完成部署配置"""
import os
import sys
import shutil
from pathlib import Path

PROJECT_DIR = Path(__file__).parent


def _input(prompt: str, default: str = "") -> str:
    val = input(f"  {prompt}").strip()
    return val if val else default


def _section(title: str):
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print(f"{'=' * 50}")


def config_ai() -> dict:
    _section("Step 1/4: AI 摘要配置")
    print("  你的报告需要 AI 来写分析，至少选一个 API。")
    print()
    print("  [1] DeepSeek  (国内，便宜，推荐)")
    print("  [2] OpenAI    (海外，稳定)")
    print("  [3] Claude    (海外，分析质量最高)")
    print("  [4] 其他兼容 API (通义千问 / 豆包 等)")
    choice = _input("选择 (1-4) [1]: ", "1")

    if choice == "1":
        key = _input("DeepSeek API Key: ")
        if not key:
            print("  !!! 未填写，将跳过 AI 摘要")
        return {
            "OPENAI_API_KEY": key,
            "OPENAI_BASE_URL": "https://api.deepseek.com",
            "AI_MODEL": _input("模型名 [deepseek-chat]: ", "deepseek-chat"),
        }
    elif choice == "2":
        key = _input("OpenAI API Key (sk-...): ")
        return {
            "OPENAI_API_KEY": key,
            "OPENAI_BASE_URL": _input("Base URL [https://api.openai.com/v1]: ", "https://api.openai.com/v1"),
            "AI_MODEL": _input("模型名 [gpt-4o]: ", "gpt-4o"),
        }
    elif choice == "3":
        key = _input("Anthropic API Key (sk-ant-...): ")
        return {
            "ANTHROPIC_API_KEY": key,
            "AI_MODEL": _input("模型名 [claude-sonnet-4-6]: ", "claude-sonnet-4-6"),
        }
    else:
        key = _input("API Key: ")
        base = _input("Base URL: ")
        return {
            "OPENAI_API_KEY": key,
            "OPENAI_BASE_URL": base,
            "AI_MODEL": _input("模型名: "),
        }


def config_email() -> dict:
    _section("Step 2/4: 邮件推送")
    print("  推荐 QQ 邮箱推送（免费，手机能收）。")
    print("  需要先在 QQ邮箱网页版 → 设置 → 账户 → 开启 SMTP → 获取授权码")
    use = _input("配置邮件推送？(y/n) [y]: ", "y")
    if use.lower() != "y":
        return {}

    user = _input("发件邮箱地址: ")
    if not user:
        return {}
    return {
        "EMAIL_SMTP_HOST": _input("SMTP 服务器 [smtp.qq.com]: ", "smtp.qq.com"),
        "EMAIL_SMTP_PORT": _input("SMTP 端口 [587]: ", "587"),
        "EMAIL_USER": user,
        "EMAIL_PASS": _input("SMTP 授权码（不是QQ密码）: "),
        "EMAIL_TO": _input("收件人（逗号分隔多个）: "),
    }


def config_other_channels() -> dict:
    _section("Step 3/4: 其他推送（可选）")
    result = {}
    if _input("配置微信推送？(y/n) [n]: ", "n").lower() == "y":
        result["SCT_KEY"] = _input("Server酱 SendKey: ")
    if _input("配置 QQ 推送？(y/n) [n]: ", "n").lower() == "y":
        result["QMSG_KEY"] = _input("Qmsg酱 Key: ")
    if _input("配置 Webhook？(y/n) [n]: ", "n").lower() == "y":
        result["WEBHOOK_URL"] = _input("Webhook URL: ")
    return result


def config_schedule() -> str:
    _section("Step 4/4: 定时运行")
    print("  [1] 仅本地 Windows 定时任务")
    print("  [2] 仅 GitHub Actions 云端运行")
    print("  [3] 两者都配（推荐）")
    return _input("选择 (1-3) [3]: ", "3")


def write_env(config: dict):
    path = PROJECT_DIR / ".env"
    backup = None
    if path.exists():
        backup = PROJECT_DIR / ".env.bak"
        shutil.copy(path, backup)
        print(f"\n  已备份旧 .env → .env.bak")

    lines = []
    for section in config.values():
        if isinstance(section, dict):
            for k, v in section.items():
                if v:
                    lines.append(f"{k}={v}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  配置已写入 .env")
    if backup:
        print(f"  旧配置备份在 .env.bak，确认无误后可删除")


def register_windows_tasks():
    if sys.platform != "win32":
        return
    if _input("\n  现在注册 Windows 定时任务？(y/n) [y]: ", "y").lower() != "y":
        return
    print()
    try:
        import subprocess
        subprocess.run([sys.executable, str(PROJECT_DIR / "register_tasks.py")])
    except Exception as e:
        print(f"  注册失败: {e}")
        print(f"  可稍后运行: python register_tasks.py")


def print_github_secrets(config: dict):
    print()
    print("  ┌─────────────────────────────────────────┐")
    print("  │  GitHub Actions 配置 (Settings→Secrets)  │")
    print("  └─────────────────────────────────────────┘")
    for section in config.values():
        if isinstance(section, dict):
            for k, v in section.items():
                if v and k not in ("EMAIL_SMTP_HOST", "EMAIL_SMTP_PORT"):
                    print(f"  {k}: {v}")


def main():
    print("=" * 50)
    print("   GitHub Trending Reporter — 一键部署向导")
    print("=" * 50)

    config = {
        "ai": config_ai(),
        "email": config_email(),
        "other": config_other_channels(),
    }
    schedule = config_schedule()

    write_env(config)

    if schedule in ("1", "3"):
        register_windows_tasks()

    if schedule in ("2", "3"):
        print_github_secrets(config)
        print(f"\n  推送代码后，GitHub Actions 即自动运行。")

    print()
    print("=" * 50)
    print("  部署完成！")
    print(f"  立即测试: python main.py daily")
    print(f"  补发当天报告: python resend_today.py")
    print(f"  查看日志: logs/")
    print("=" * 50)


if __name__ == "__main__":
    main()
