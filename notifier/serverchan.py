import httpx

from .base import BaseNotifier

SCT_URL = "https://sctapi.ftqq.com/{key}.send"


class ServerChanNotifier(BaseNotifier):
    """Server酱：推送到微信。注册 https://sct.ftqq.com 获取 SendKey"""

    def __init__(self, send_key: str):
        self.url = SCT_URL.format(key=send_key)

    def send(self, title: str, content: str) -> bool:
        try:
            with httpx.Client(timeout=15, verify=False) as client:
                resp = client.post(self.url, data={
                    "title": title,
                    "desp": content[:65536],  # Server酱限制 64KB
                })
                if resp.status_code == 200:
                    return True
                print(f"[ServerChan] 返回异常: {resp.status_code} {resp.text}")
                return False
        except Exception as e:
            print(f"[ServerChan] 发送失败: {e}")
            return False
