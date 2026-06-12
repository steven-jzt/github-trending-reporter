import re
from typing import Literal

import httpx
from bs4 import BeautifulSoup

from .models import Repo

Period = Literal["daily", "weekly"]

TRENDING_URL = "https://github.com/trending"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def _parse_number(text: str) -> int:
    """'1,234' -> 1234, '12.3k' -> 12300"""
    t = text.strip().lower().replace(",", "").replace(" ", "")
    if not t:
        return 0
    if "k" in t:
        return int(float(t.replace("k", "")) * 1000)
    try:
        return int(float(t))
    except ValueError:
        return 0


def _fetch_html(url: str) -> str:
    """获取页面 HTML，自动处理 SSL 问题"""
    with httpx.Client(
        headers=HEADERS, follow_redirects=True, timeout=30, verify=False
    ) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return resp.text


def fetch_trending(period: Period = "daily", count: int = 25) -> list[Repo]:
    """抓取 GitHub Trending 仓库列表。period: daily | weekly"""
    url = f"{TRENDING_URL}?since={period}"

    try:
        html = _fetch_html(url)
    except httpx.HTTPError:
        # 如果 verify=False 也失败，再试一次不带 header 魔法的
        html = _fetch_html(url)

    soup = BeautifulSoup(html, "html.parser")
    repos: list[Repo] = []

    for article in soup.find_all("article", class_="Box-row"):
        if len(repos) >= count:
            break
        try:
            # --- 仓库名和 owner ---
            h2 = article.find("h2", class_="h3")
            if not h2 or not h2.a:
                continue
            href = h2.a.get("href", "").strip()
            raw_name = h2.a.get_text(" ", strip=True)
            # "owner / reponame" -> owner, reponame
            parts = [p.strip() for p in raw_name.replace("\n", " ").split("/")]
            if len(parts) >= 2:
                owner, name = parts[0], parts[1].split()[0]
            else:
                owner, name = parts[0], parts[0]

            # --- 描述 ---
            desc_tag = article.find("p")
            description = desc_tag.get_text(strip=True) if desc_tag else ""

            # --- 语言 ---
            lang_tag = article.find("span", itemprop="programmingLanguage")
            language = lang_tag.get_text(strip=True) if lang_tag else ""

            # --- 总 stars ---
            total_stars = 0
            # 找 stargazers 链接
            for a_tag in article.find_all("a", href=True):
                if "/stargazers" in a_tag["href"]:
                    nums = re.findall(r"[\d,]+", a_tag.get_text(strip=True))
                    if nums:
                        total_stars = _parse_number(nums[0])
                        break

            # --- 今日/本周 stars ---
            stars_period = 0
            for span in article.find_all("span", class_="d-inline-block"):
                text = span.get_text(strip=True)
                if "star" in text.lower():
                    nums = re.findall(r"[\d,]+", text)
                    if nums:
                        stars_period = _parse_number(nums[0])
                        break

            repos.append(Repo(
                owner=owner,
                name=name,
                description=description,
                language=language,
                total_stars=total_stars,
                stars_period=stars_period,
                url=f"https://github.com{href}",
            ))
        except Exception:
            continue

    return repos
