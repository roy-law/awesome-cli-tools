"""Discover trending CLI-related repos on GitHub using the search API."""

import os
from datetime import datetime, timedelta

import httpx

from pipeline.sources.github_topics import GitHubRepo


async def search_github_trending(
    languages: list[str] | None = None,
    days: int = 30,
    per_page: int = 50,
) -> list[GitHubRepo]:
    """Find repos created in the last N days with high star counts."""
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    languages = languages or [""]
    seen: set[str] = set()
    repos: list[GitHubRepo] = []

    async with httpx.AsyncClient(headers=headers, timeout=30) as client:
        for lang in languages:
            q = f"created:>{since} stars:>50"
            if lang:
                q += f" language:{lang}"

            params = {
                "q": q,
                "sort": "stars",
                "order": "desc",
                "per_page": per_page,
            }
            response = await client.get(
                "https://api.github.com/search/repositories",
                params=params,
            )
            response.raise_for_status()

            for item in response.json().get("items", []):
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
