import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import markdown

from .base import BaseNotifier
from log import get_logger
from retry import with_retry

MD = markdown.Markdown(extensions=["tables", "fenced_code"])


class EmailNotifier(BaseNotifier):
    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        user: str,
        password: str,
        to: list[str],
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.user = user
        self.password = password
        self.to = to

    def send(self, title: str, content: str) -> bool:
        html = MD.convert(content)
        styled = (
            '<html><body style="font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif;'
            'font-size:15px;line-height:1.7;color:#24292e;padding:20px;max-width:720px;">'
            + html +
            "</body></html>"
        )
        msg = MIMEMultipart("alternative")
        msg["Subject"] = title
        msg["From"] = self.user
        msg["To"] = ", ".join(self.to)
        msg.attach(MIMEText(styled, "html", "utf-8"))

        def _do_send():
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=15) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.sendmail(self.user, self.to, msg.as_string())

        try:
            with_retry(_do_send, "邮件发送", max_retries=3, delay=10)
            return True
        except Exception as e:
            log = get_logger("email")
            log.error(f"发送失败 (已重试): {e}")
            return False
