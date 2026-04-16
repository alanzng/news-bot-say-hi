import logging
import requests
from bs4 import BeautifulSoup
from src.base import DataSource

logger = logging.getLogger(__name__)

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; news-bot/1.0)"}
_PERIOD_LABELS = {"daily": "today", "weekly": "this week", "monthly": "this month"}


class GitHubTrendingSource(DataSource):
    name = "github-trending"
    default_schedule = "0 9 * * *"

    def __init__(self, language: str = "", since: str = "daily", limit: int = 5) -> None:
        self.language = language
        self.since = since
        self.limit = limit

    def fetch(self) -> list[dict]:
        path = f"https://github.com/trending/{self.language}".rstrip("/")
        resp = requests.get(path, params={"since": self.since}, headers=_HEADERS, timeout=15)
        if resp.status_code != 200:
            raise RuntimeError(f"GitHub returned HTTP {resp.status_code}")

        soup = BeautifulSoup(resp.text, "html.parser")
        articles = soup.find_all("article", {"class": "Box-row"})
        if not articles:
            logger.warning("[github-trending] no repository elements found in HTML")
            return []

        records = []
        for i, article in enumerate(articles[: self.limit], start=1):
            repo_el = article.find("h2")
            repo = repo_el.get_text(strip=True).replace(" ", "").replace("\n", "") if repo_el else "unknown"
            desc_el = article.find("p")
            description = desc_el.get_text(strip=True) if desc_el else ""
            stars_el = article.find("a", href=lambda h: h and h.endswith("/stargazers"))
            stars = stars_el.get_text(strip=True) if stars_el else "?"
            lang_el = article.find("span", {"itemprop": "programmingLanguage"})
            language = lang_el.get_text(strip=True) if lang_el else ""
            records.append({
                "rank": i,
                "repo": repo,
                "description": description,
                "language": language,
                "stars": stars,
            })
        return records

    def format(self, records: list[dict]) -> str:
        if not records:
            return ""
        label = _PERIOD_LABELS.get(self.since, self.since)

        def row(r: dict) -> str:
            parts = [f"{r['rank']}. <b>{r['repo']}</b> ⭐ {r['stars']}"]
            if r["language"]:
                parts.append(f"   🔤 {r['language']}")
            if r["description"]:
                parts.append(f"   {r['description']}")
            return "\n".join(parts)

        lines = [
            f"🐙 <b>GitHub Trending</b> ({label})",
            "",
        ]
        lines.extend(row(r) for r in records)
        lines.append("")
        lines.append("🔗 Nguồn: github.com/trending")

        return "\n".join(lines)
