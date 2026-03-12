from unittest.mock import AsyncMock, patch

import pytest

from pipeline.discover import discover_candidates
from pipeline.sources.github_topics import GitHubRepo


def _make_repo(name: str, stars: int = 1000) -> GitHubRepo:
    return GitHubRepo(
        full_name=name,
        url=f"https://github.com/{name}",
        description=f"Description of {name}",
        stars=stars,
        language="Rust",
        license="MIT",
        pushed_at="2026-03-01T00:00:00Z",
        topics=["cli"],
    )


@pytest.mark.asyncio
@patch("pipeline.discover.search_github_topics", new_callable=AsyncMock)
@patch("pipeline.discover.search_github_trending", new_callable=AsyncMock)
async def test_discover_merges_sources(mock_trending, mock_topics):
    mock_topics.return_value = [_make_repo("owner/tool-a")]
    mock_trending.return_value = [_make_repo("owner/tool-b")]
    candidates = await discover_candidates(existing_repos=set())
    names = {c.full_name for c in candidates}
    assert "owner/tool-a" in names
    assert "owner/tool-b" in names


@pytest.mark.asyncio
@patch("pipeline.discover.search_github_topics", new_callable=AsyncMock)
@patch("pipeline.discover.search_github_trending", new_callable=AsyncMock)
async def test_discover_excludes_existing(mock_trending, mock_topics):
    mock_topics.return_value = [_make_repo("owner/existing")]
    mock_trending.return_value = []
    candidates = await discover_candidates(existing_repos={"owner/existing"})
    assert len(candidates) == 0


@pytest.mark.asyncio
@patch("pipeline.discover.search_github_topics", new_callable=AsyncMock)
@patch("pipeline.discover.search_github_trending", new_callable=AsyncMock)
async def test_discover_deduplicates_across_sources(mock_trending, mock_topics):
    repo = _make_repo("owner/tool-a")
    mock_topics.return_value = [repo]
    mock_trending.return_value = [repo]
    candidates = await discover_candidates(existing_repos=set())
    assert len(candidates) == 1
