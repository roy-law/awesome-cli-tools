"""Gate 0: Discover candidate CLI tools from multiple sources."""

from pipeline.data import load_sources
from pipeline.sources.github_topics import GitHubRepo, search_github_topics
from pipeline.sources.github_trending import search_github_trending


async def discover_candidates(
    existing_repos: set[str] | None = None,
    sources_config: dict | None = None,
) -> list[GitHubRepo]:
    """Fetch candidates from all enabled sources, dedup against existing tools."""
    if existing_repos is None:
        existing_repos = set()
    if sources_config is None:
        sources_config = load_sources()

    seen: set[str] = set(existing_repos)
    candidates: list[GitHubRepo] = []

    src = sources_config.get("sources", {})

    # GitHub Topics
    topics_cfg = src.get("github_topics", {})
    if topics_cfg.get("enabled", False):
        repos = await search_github_topics(
            topics=topics_cfg.get("topics", ["cli"]),
            per_topic_limit=topics_cfg.get("per_topic_limit", 100),
        )
        for repo in repos:
            if repo.full_name not in seen:
                seen.add(repo.full_name)
                candidates.append(repo)

    # GitHub Trending
    trending_cfg = src.get("github_trending", {})
    if trending_cfg.get("enabled", False):
        repos = await search_github_trending(
            languages=trending_cfg.get("languages", [""]),
        )
        for repo in repos:
            if repo.full_name not in seen:
                seen.add(repo.full_name)
                candidates.append(repo)

    # Future: hackernews, reddit, awesome_lists — add here when enabled

    return candidates
