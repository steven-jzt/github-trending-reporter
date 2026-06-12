from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class Repo:
    owner: str
    name: str
    description: str
    language: str
    total_stars: int
    stars_period: int  # 今日/本周新增
    url: str

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.name}"


@dataclass
class Report:
    period: str  # "daily" | "weekly"
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    repos: list[Repo] = field(default_factory=list)
    content: str = ""

    @property
    def title(self) -> str:
        label = "每日" if self.period == "daily" else "每周"
        return f"GitHub Trending {label}报告 ({self.date})"

    def save(self, base_dir: str = "reports") -> Path:
        p = Path(base_dir)
        p.mkdir(parents=True, exist_ok=True)
        filename = f"github-trending-{self.period}-{self.date}.md"
        filepath = p / filename
        filepath.write_text(self.content, encoding="utf-8")
        return filepath
