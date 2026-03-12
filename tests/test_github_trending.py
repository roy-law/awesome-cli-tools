# tests/test_github_trending.py
import httpx
import pytest
import respx

from pipeline.sources.github_trending import search_github_trending, GitHubRepo


@respx.mock
@pytest.mark.asyncio
async def test_search_trending_uses_created_filter():
    """Trending = recently created repos with high stars, queried via search API."""
    respx.get("https://api.github.com/search/repositories").mock(
        return_value=httpx.Response(200, json={"items": []})
    )
    await search_github_trending(languages=["rust"])
    call = respx.calls[0]
    query = str(call.request.url)
    assert "created" in query


@respx.mock
@pytest.mark.asyncio
async def test_search_trending_parses_repos():
    mock_response = {
        "items": [
            {
                "full_name": "astral-sh/uv",
                "html_url": "https://github.com/astral-sh/uv",
                "description": "Fast Python package manager",
                "stargazers_count": 30000,
                "fork": False,
                "archived": False,
                "language": "Rust",
                "license": {"spdx_id": "MIT"},
                "pushed_at": "2026-03-10T00:00:00Z",
                "topics": ["python", "package-manager"],
            }
        ]
    }
    respx.get("https://api.github.com/search/repositories").mock(
        return_value=httpx.Response(200, json=mock_response)
    )
    repos = await search_github_trending(languages=["rust"])
    assert len(repos) == 1
    assert repos[0].full_name == "astral-sh/uv"
