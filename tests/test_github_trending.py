# tests/test_github_trending.py
import httpx
import pytest
import respx

from pipeline.sources.github_trending import search_github_trending, GitHubRepo


@respx.mock
@pytest.mark.asyncio
async def test_search_trending_uses_dual_strategy():
    """Trending uses both created and pushed strategies."""
    respx.get("https://api.github.com/search/repositories").mock(
        return_value=httpx.Response(200, json={"items": []})
    )
    await search_github_trending(languages=["rust"])
    # With dual strategy, there should be 2 API calls per language
    assert len(respx.calls) == 2
    queries = [str(call.request.url) for call in respx.calls]
    assert any("created" in q for q in queries)
    assert any("pushed" in q for q in queries)


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


@respx.mock
@pytest.mark.asyncio
async def test_search_trending_deduplicates_across_strategies():
    """Same repo returned by both strategies should appear only once."""
    item = {
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
    respx.get("https://api.github.com/search/repositories").mock(
        return_value=httpx.Response(200, json={"items": [item]})
    )
    repos = await search_github_trending(languages=["rust"])
    assert len(repos) == 1
