import httpx
import pytest
import respx

from pipeline.sources.github_topics import search_github_topics, GitHubRepo


@respx.mock
@pytest.mark.asyncio
async def test_search_github_topics_parses_response():
    mock_response = {
        "items": [
            {
                "full_name": "BurntSushi/ripgrep",
                "html_url": "https://github.com/BurntSushi/ripgrep",
                "description": "ripgrep recursively searches directories",
                "stargazers_count": 48000,
                "fork": False,
                "archived": False,
                "language": "Rust",
                "license": {"spdx_id": "MIT"},
                "pushed_at": "2026-03-01T00:00:00Z",
                "topics": ["cli", "grep", "search"],
            }
        ]
    }
    respx.get("https://api.github.com/search/repositories").mock(
        return_value=httpx.Response(200, json=mock_response)
    )
    repos = await search_github_topics(topics=["cli"], per_topic_limit=10)
    assert len(repos) == 1
    assert repos[0].full_name == "BurntSushi/ripgrep"
    assert repos[0].stars == 48000


@respx.mock
@pytest.mark.asyncio
async def test_search_github_topics_skips_forks():
    mock_response = {
        "items": [
            {
                "full_name": "fork/ripgrep",
                "html_url": "https://github.com/fork/ripgrep",
                "description": "A fork",
                "stargazers_count": 100,
                "fork": True,
                "archived": False,
                "language": "Rust",
                "license": None,
                "pushed_at": "2026-03-01T00:00:00Z",
                "topics": [],
            }
        ]
    }
    respx.get("https://api.github.com/search/repositories").mock(
        return_value=httpx.Response(200, json=mock_response)
    )
    repos = await search_github_topics(topics=["cli"], per_topic_limit=10)
    assert len(repos) == 0


@respx.mock
@pytest.mark.asyncio
async def test_search_github_topics_deduplicates():
    item = {
        "full_name": "BurntSushi/ripgrep",
        "html_url": "https://github.com/BurntSushi/ripgrep",
        "description": "ripgrep",
        "stargazers_count": 48000,
        "fork": False,
        "archived": False,
        "language": "Rust",
        "license": {"spdx_id": "MIT"},
        "pushed_at": "2026-03-01T00:00:00Z",
        "topics": ["cli"],
    }
    respx.get("https://api.github.com/search/repositories").mock(
        return_value=httpx.Response(200, json={"items": [item]})
    )
    repos = await search_github_topics(topics=["cli", "terminal"], per_topic_limit=10)
    assert len(repos) == 1
