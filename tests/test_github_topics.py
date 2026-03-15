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


def test_looks_like_cli_tool_positive():
    repo = GitHubRepo(
        full_name="owner/tool",
        url="https://github.com/owner/tool",
        description="A fast cli tool for searching files",
        stars=100,
        language="Rust",
        license="MIT",
        pushed_at="2026-03-01T00:00:00Z",
        topics=["cli"],
    )
    assert repo.looks_like_cli_tool() is True


def test_looks_like_cli_tool_negative():
    repo = GitHubRepo(
        full_name="owner/lib",
        url="https://github.com/owner/lib",
        description="A web framework for building APIs",
        stars=100,
        language="Python",
        license="MIT",
        pushed_at="2026-03-01T00:00:00Z",
        topics=["web", "api"],
    )
    assert repo.looks_like_cli_tool() is False


@respx.mock
@pytest.mark.asyncio
async def test_search_github_topics_keyword_queries():
    """Keyword-based strategy produces results alongside topic strategy."""
    item1 = {
        "full_name": "owner/topic-tool",
        "html_url": "https://github.com/owner/topic-tool",
        "description": "A CLI tool found via topic",
        "stargazers_count": 500,
        "fork": False,
        "archived": False,
        "language": "Go",
        "license": {"spdx_id": "Apache-2.0"},
        "pushed_at": "2026-03-01T00:00:00Z",
        "topics": ["cli"],
    }
    item2 = {
        "full_name": "owner/keyword-tool",
        "html_url": "https://github.com/owner/keyword-tool",
        "description": "A cli tool for linting",
        "stargazers_count": 300,
        "fork": False,
        "archived": False,
        "language": "Python",
        "license": None,
        "pushed_at": "2026-03-01T00:00:00Z",
        "topics": [],
    }
    # First call returns topic result, subsequent calls return keyword result
    route = respx.get("https://api.github.com/search/repositories")
    route.side_effect = [
        httpx.Response(200, json={"items": [item1]}),
        httpx.Response(200, json={"items": [item2]}),
        httpx.Response(200, json={"items": []}),
        httpx.Response(200, json={"items": []}),
        httpx.Response(200, json={"items": []}),
    ]
    repos = await search_github_topics(topics=["cli"], per_topic_limit=10)
    names = {r.full_name for r in repos}
    assert "owner/topic-tool" in names
    assert "owner/keyword-tool" in names
