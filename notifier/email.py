import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import markdown

from .base import BaseNotifier

MD = markdown.Markdown(extensions=["tables", "fenced_code"])


class EmailNotifier(BaseNotifier):
    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        user: str,
        password: str,
        to: str,
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.user = user
        self.password = password
        self.to = to

    def send(self, title: str, content: str) -> bool:
        html = MD.convert(content)
        # 内联样式，让 QQ 邮箱等客户端渲染更美观
        styled = (
            '<html><body style="font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif;'
            'font-size:15px;line-height:1.7;color:#24292e;padding:20px;max-width:720px;">'
            + html +
            "</body></html>"
        )
        msg = MIMEMultipart("alternative")
        msg["Subject"] = title
        msg["From"] = self.user
        msg["To"] = self.to
        msg.attach(MIMEText(styled, "html", "utf-8"))

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=15) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.sendmail(self.user, [self.to], msg.as_string())
            return True
        except Exception as e:
            print(f"[EmailNotifier] 发送失败: {e}")
            return False
