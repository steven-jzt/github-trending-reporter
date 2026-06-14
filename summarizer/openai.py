from openai import OpenAI

from .base import BaseSummarizer
from .utils import SYSTEM_PROMPT, format_repos_text
from trending.models import Repo


class OpenAISummarizer(BaseSummarizer):
    def __init__(self, api_key: str, model: str = "gpt-4o", base_url: str | None = None):
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = OpenAI(**kwargs)
        self.model = model

    def summarize(self, repos: list[Repo], period: str) -> str:
        labels = {"daily": "今日", "weekly": "本周", "monthly": "本月"}
        label = labels.get(period, "本周")
        repo_text = format_repos_text(repos)

        user_msg = f"以下是 GitHub Trending {label}的仓库列表（共 {len(repos)} 个）：\n\n{repo_text}\n\n请据此生成{label}GitHub Trending 技术报告。"

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            max_tokens=4096,
        )
        return resp.choices[0].message.content or ""
