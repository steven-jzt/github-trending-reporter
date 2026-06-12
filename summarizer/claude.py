from anthropic import Anthropic

from .base import BaseSummarizer
from .utils import SYSTEM_PROMPT, format_repos_text
from trending.models import Repo


class ClaudeSummarizer(BaseSummarizer):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6", base_url: str | None = None):
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = Anthropic(**kwargs)
        self.model = model

    def summarize(self, repos: list[Repo], period: str) -> str:
        label = "今日" if period == "daily" else "本周"
        repo_text = format_repos_text(repos)

        user_msg = f"以下是 GitHub Trending {label}的仓库列表（共 {len(repos)} 个）：\n\n{repo_text}\n\n请据此生成{label}GitHub Trending 技术报告。"

        resp = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        return resp.content[0].text
