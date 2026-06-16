"""启动前预检：环境变量、API连通性、SMTP连通性"""
import os
import smtplib
import socket
from dotenv import load_dotenv
from log import get_logger

load_dotenv()
log = get_logger("validate")


def check_config() -> list[str]:
    """检查所有配置，返回问题列表。返回空列表表示一切正常。"""
    issues: list[str] = []

    # --- AI API ---
    api_type = ""
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    ai_model = os.getenv("AI_MODEL", "").strip()

    if anthropic_key:
        api_type = "Anthropic"
    elif openai_key:
        api_type = "OpenAI 兼容"
    else:
        issues.append("未配置任何 AI API key (ANTHROPIC_API_KEY 或 OPENAI_API_KEY)")

    if api_type:
        if ai_model:
            log.info(f"AI: {api_type} / 模型: {ai_model}")
        else:
            log.warn("未设置 AI_MODEL，将使用默认模型")

    # --- 推送通道 ---
    has_any = False
    if os.getenv("EMAIL_USER", "").strip():
        has_any = True
        email_to = [a.strip() for a in os.getenv("EMAIL_TO", "").split(",") if a.strip()]
        if email_to:
            log.info(f"邮件: {os.getenv('EMAIL_USER', '').strip()} -> {len(email_to)} 个收件人")
        else:
            issues.append("EMAIL_USER 已设置但 EMAIL_TO 为空")
    if os.getenv("SCT_KEY", "").strip():
        has_any = True
        log.info("微信推送 (Server酱): 已配置")
    if os.getenv("QMSG_KEY", "").strip():
        has_any = True
        log.info("QQ推送 (Qmsg酱): 已配置")
    if os.getenv("WEBHOOK_URL", "").strip():
        has_any = True
        log.info("Webhook: 已配置")

    if not has_any:
        issues.append("未配置任何推送通道 (EMAIL_USER / SCT_KEY / QMSG_KEY / WEBHOOK_URL)，报告仅本地保存")

    return issues


def check_api_connectivity() -> list[str]:
    """检测 API 端点连通性，返回问题列表。"""
    issues: list[str] = []
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "").strip()

    if openai_key:
        base_url = os.getenv("OPENAI_BASE_URL", "").strip()
        if base_url:
            host = base_url.replace("https://", "").replace("http://", "").split("/")[0].split(":")[0]
            ok, err = _tcp_check(host, 443)
            if ok:
                log.ok(f"API 连通: {base_url}")
            else:
                msg = f"无法连接 AI API: {base_url} ({err})"
                issues.append(msg)
                log.error(msg)

    if anthropic_key:
        base_url = os.getenv("ANTHROPIC_BASE_URL", "api.anthropic.com").strip()
        host = base_url.replace("https://", "").replace("http://", "").split("/")[0].split(":")[0]
        ok, err = _tcp_check(host, 443)
        if ok:
            log.ok(f"API 连通: {host}")
        else:
            msg = f"无法连接 Anthropic API: {host} ({err})"
            issues.append(msg)
            log.error(msg)

    return issues


def check_smtp_connectivity() -> list[str]:
    """检测 SMTP 连通性。"""
    issues: list[str] = []
    email_user = os.getenv("EMAIL_USER", "").strip()
    if not email_user:
        return issues

    host = os.getenv("EMAIL_SMTP_HOST", "smtp.qq.com").strip()
    port = int(os.getenv("EMAIL_SMTP_PORT", "587").strip())

    try:
        with smtplib.SMTP(host, port, timeout=10) as server:
            server.starttls()
            server.login(email_user, os.getenv("EMAIL_PASS", "").strip())
        log.ok(f"SMTP 连通: {host}:{port}")
    except smtplib.SMTPAuthenticationError:
        issues.append(f"SMTP 认证失败: {host}:{port} (EMAIL_PASS 授权码是否正确？)")
    except socket.timeout:
        issues.append(f"SMTP 连接超时: {host}:{port} (网络是否可达？)")
    except Exception as e:
        issues.append(f"SMTP 连接失败: {host}:{port} ({e})")

    return issues


def _tcp_check(host: str, port: int, timeout: float = 5.0) -> tuple[bool, str]:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, ""
    except socket.timeout:
        return False, "连接超时"
    except socket.gaierror:
        return False, "DNS 解析失败"
    except Exception as e:
        return False, str(e)


def run_preflight() -> bool:
    """执行所有预检，打印结果。返回 True 表示通过。"""
    log.info("===== 配置预检 =====")

    config_issues = check_config()
    api_issues = check_api_connectivity()
    smtp_issues = check_smtp_connectivity()

    all_issues = config_issues + api_issues + smtp_issues

    if all_issues:
        log.error(f"发现 {len(all_issues)} 个问题:")
        for i, issue in enumerate(all_issues, 1):
            log.error(f"  {i}. {issue}")
        log.info("===== 预检失败 =====")
        return False
    else:
        log.ok("所有检查通过")
        log.info("===== 预检完成 =====")
        return True


if __name__ == "__main__":
    ok = run_preflight()
    print(f"\n预检结果: {'通过' if ok else '失败'}")
