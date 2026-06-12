import httpx

from .base import BaseNotifier


class WebhookNotifier(BaseNotifier):
    """通用 Webhook：支持企业微信机器人、Discord、Slack 等。
    用户提供 webhook_url，POST JSON body: {"title": ..., "content": ...}
    如需自定义格式，可继承此类重写 _build_payload。
    """

    def __init__(self, url: str):
        self.url = url

    def send(self, title: str, content: str) -> bool:
        try:
            with httpx.Client(timeout=15, verify=False) as client:
                resp = client.post(self.url, json=self._build_payload(title, content))
                if resp.status_code in (200, 204):
                    return True
                print(f"[Webhook] 返回异常: {resp.status_code}")
                return False
        except Exception as e:
            print(f"[Webhook] 发送失败: {e}")
            return False

    @staticmethod
    def _build_payload(title: str, content: str) -> dict:
        return {"title": title, "content": content}
