from abc import ABC, abstractmethod


class BaseNotifier(ABC):
    """推送通道抽象基类。实现 send 即可接入。"""

    @abstractmethod
    def send(self, title: str, content: str) -> bool:
        """发送通知，成功返回 True"""
        ...
