import os

from dotenv import load_dotenv

load_dotenv()


def get_summarizer():
    """根据 .env 配置返回激活的 AI 摘要器，未配置则返回 None"""
    # 优先 Claude
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if anthropic_key:
        from summarizer.claude import ClaudeSummarizer
        model = os.getenv("AI_MODEL", "claude-sonnet-4-6").strip()
        base_url = os.getenv("ANTHROPIC_BASE_URL", "").strip() or None
        return ClaudeSummarizer(api_key=anthropic_key, model=model, base_url=base_url)

    # 其次 OpenAI
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    if openai_key:
        from summarizer.openai import OpenAISummarizer
        model = os.getenv("AI_MODEL", "gpt-4o").strip()
        base_url = os.getenv("OPENAI_BASE_URL", "").strip() or None
        return OpenAISummarizer(api_key=openai_key, model=model, base_url=base_url)

    return None


def get_notifiers():
    """根据 .env 配置返回所有激活的推送通道"""
    notifiers = []

    # 邮件
    email_user = os.getenv("EMAIL_USER", "").strip()
    if email_user:
        from notifier.email import EmailNotifier
        notifiers.append(EmailNotifier(
            smtp_host=os.getenv("EMAIL_SMTP_HOST", "smtp.qq.com").strip(),
            smtp_port=int(os.getenv("EMAIL_SMTP_PORT", "587").strip()),
            user=email_user,
            password=os.getenv("EMAIL_PASS", "").strip(),
            to=[a.strip() for a in os.getenv("EMAIL_TO", "").split(",") if a.strip()],
        ))

    # 微信 Server酱
    sct_key = os.getenv("SCT_KEY", "").strip()
    if sct_key:
        from notifier.serverchan import ServerChanNotifier
        notifiers.append(ServerChanNotifier(send_key=sct_key))

    # QQ Qmsg酱
    qmsg_key = os.getenv("QMSG_KEY", "").strip()
    if qmsg_key:
        from notifier.qmsg import QmsgNotifier
        notifiers.append(QmsgNotifier(key=qmsg_key))

    # 通用 Webhook
    webhook_url = os.getenv("WEBHOOK_URL", "").strip()
    if webhook_url:
        from notifier.webhook import WebhookNotifier
        notifiers.append(WebhookNotifier(url=webhook_url))

    return notifiers
