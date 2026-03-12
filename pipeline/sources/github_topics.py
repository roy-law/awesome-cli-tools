"""Discover CLI tools by searching GitHub topics."""

import os
from dataclasses import dataclass

import httpx


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
        for topic in topics:
            params = {
                "q": f"topic:{topic}",
                "sort": "stars",
                "order": "desc",
                "per_page": min(per_topic_limit, 100),
            }
            response = await client.get(
                "https://api.github.com/search/repositories",
                params=params,
            )
            response.raise_for_status()
            data = response.json()

            for item in data.get("items", []):
                if item["fork"] or item["archived"]:
                    continue
                if item["full_name"] in seen:
                    continue
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

    return repos
