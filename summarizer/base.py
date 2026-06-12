from abc import ABC, abstractmethod

from trending.models import Repo


class BaseSummarizer(ABC):
    """AI 摘要抽象基类。用户接入自己的 API key 即可使用。"""

    @abstractmethod
    def summarize(self, repos: list[Repo], period: str) -> str:
        """生成 Markdown 格式的报告，period 为 'daily' 或 'weekly'"""
        ...
