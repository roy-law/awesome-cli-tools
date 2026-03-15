"""Discover CLI tools by searching GitHub topics and keywords."""

import os
from dataclasses import dataclass

import httpx

CLI_KEYWORDS = {
    "cli", "command-line", "command line", "terminal", "tui",
    "console", "shell", "curses", "ncurses", "command-line-tool",
    "cli-app", "cli-tool", "terminal-app",
}


@dataclass
class GitHubRepo:
    full_name: str
    url: str
    description: str
    stars: int
    language: str | None
    license: str | None
    pushed_at: str
    topics: list[str]

    def looks_like_cli_tool(self) -> bool:
        """Heuristic check if this repo is likely a CLI/TUI tool."""
        text = f"{self.description} {' '.join(self.topics)}".lower()
        return any(kw in text for kw in CLI_KEYWORDS)


async def search_github_topics(
    topics: list[str],
    per_topic_limit: int = 100,
) -> list[GitHubRepo]:
    """Search GitHub for repos matching given topics, deduplicated."""
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    seen: set[str] = set()
    repos: list[GitHubRepo] = []

    async with httpx.AsyncClient(headers=headers, timeout=30) as client:
        # Strategy 1: Topic-based search
        for topic in topics:
            pages = min(3, (per_topic_limit + 99) // 100)
            for page in range(1, pages + 1):
                params = {
                    "q": f"topic:{topic}",
                    "sort": "stars",
                    "order": "desc",
                    "per_page": min(per_topic_limit, 100),
                    "page": page,
                }
                response = await client.get(
                    "https://api.github.com/search/repositories",
                    params=params,
                )
                if response.status_code == 403:  # rate limited
                    break
                response.raise_for_status()
                items = response.json().get("items", [])
                if not items:
                    break

                for item in items:
                    _maybe_add(item, seen, repos)

        # Strategy 2: Keyword-based search in descriptions
        keyword_queries = [
            '"cli tool" stars:>50',
            '"command-line tool" stars:>50',
            '"terminal app" stars:>50',
            '"tui" "terminal" stars:>50',
        ]
        for q in keyword_queries:
            params = {
                "q": q,
                "sort": "stars",
                "order": "desc",
                "per_page": 100,
            }
            response = await client.get(
                "https://api.github.com/search/repositories",
                params=params,
            )
            if response.status_code == 403:
                break
            response.raise_for_status()
            for item in response.json().get("items", []):
                _maybe_add(item, seen, repos)

    return repos


def _maybe_add(item: dict, seen: set[str], repos: list[GitHubRepo]) -> None:
    """Add a repo to the list if it passes basic filters."""
    if item["fork"] or item["archived"]:
        return
    if item["full_name"] in seen:
        return
    seen.add(item["full_name"])

    license_id = None
    if item.get("license"):
        license_id = item["license"].get("spdx_id")

    repos.append(
        GitHubRepo(
            full_name=item["full_name"],
            url=item["html_url"],
            description=item.get("description") or "",
            stars=item["stargazers_count"],
            language=item.get("language"),
            license=license_id,
            pushed_at=item["pushed_at"],
            topics=item.get("topics", []),
        )
    )
