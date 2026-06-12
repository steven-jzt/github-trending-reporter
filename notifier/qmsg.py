import httpx

from .base import BaseNotifier

QMSG_URL = "https://qmsg.zendee.cn/send/{key}"


class QmsgNotifier(BaseNotifier):
    """Qmsg酱：推送到QQ。注册 https://qmsg.zendee.cn 获取 Key"""

    def __init__(self, key: str):
        self.url = QMSG_URL.format(key=key)

    def send(self, title: str, content: str) -> bool:
        # Qmsg 消息体合并 title + content
        text = f"{title}\n\n{content}"[:15000]
        try:
            with httpx.Client(timeout=15, verify=False) as client:
                resp = client.post(self.url, data={
                    "msg": text,
                })
                data = resp.json()
                if data.get("success"):
                    return True
                print(f"[Qmsg] 返回异常: {data}")
                return False
        except Exception as e:
            print(f"[Qmsg] 发送失败: {e}")
            return False
