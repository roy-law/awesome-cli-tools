import json
from unittest.mock import AsyncMock, patch

import pytest

from pipeline.evaluate import evaluate_repo, EvalResult
from pipeline.score import ScoredRepo
from pipeline.sources.github_topics import GitHubRepo


def _make_scored_repo() -> ScoredRepo:
    repo = GitHubRepo(
        full_name="sharkdp/bat",
        url="https://github.com/sharkdp/bat",
        description="A cat clone with wings",
        stars=50000,
        language="Rust",
        license="MIT",
        pushed_at="2026-03-01T00:00:00Z",
        topics=["cli", "terminal"],
    )
    return ScoredRepo(repo=repo, score=85.0)


@pytest.mark.asyncio
async def test_evaluate_repo_accept():
    llm_response = json.dumps({
        "is_cli_tool": True,
        "quality_score": 9,
        "category": "file-management",
        "description": "A cat(1) clone with syntax highlighting and Git integration",
        "reasoning": "Well-known, high-quality CLI tool",
    })
    mock_llm = AsyncMock()
    mock_llm.complete = AsyncMock(return_value=llm_response)

    result = await evaluate_repo(
        _make_scored_repo(),
        existing_descriptions=[],
        categories=["search", "file-management", "shell"],
        llm=mock_llm,
        readme="# bat\nA cat(1) clone with syntax highlighting.",
    )
    assert result.accepted is True
    assert result.category == "file-management"
    assert result.quality_score == 9


@pytest.mark.asyncio
async def test_evaluate_repo_reject_low_quality():
    llm_response = json.dumps({
        "is_cli_tool": True,
        "quality_score": 3,
        "category": "misc",
        "description": "Some tool",
        "reasoning": "Low quality, poorly documented",
    })
    mock_llm = AsyncMock()
    mock_llm.complete = AsyncMock(return_value=llm_response)

    result = await evaluate_repo(
        _make_scored_repo(),
        existing_descriptions=[],
        categories=["misc"],
        llm=mock_llm,
        readme="# some tool",
    )
    assert result.accepted is False


@pytest.mark.asyncio
async def test_evaluate_repo_reject_not_cli():
    llm_response = json.dumps({
        "is_cli_tool": False,
        "quality_score": 8,
        "category": "misc",
        "description": "A web framework",
        "reasoning": "Not a CLI tool",
    })
    mock_llm = AsyncMock()
    mock_llm.complete = AsyncMock(return_value=llm_response)

    result = await evaluate_repo(
        _make_scored_repo(),
        existing_descriptions=[],
        categories=["misc"],
        llm=mock_llm,
        readme="# some tool",
    )
    assert result.accepted is False
