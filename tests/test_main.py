# tests/test_main.py
from unittest.mock import AsyncMock, patch, MagicMock
import json

import pytest

from pipeline.main import run_pipeline
from pipeline.sources.github_topics import GitHubRepo
from pipeline.score import ScoredRepo
from pipeline.evaluate import EvalResult


@pytest.mark.asyncio
@patch("pipeline.main.create_pr")
@patch("pipeline.main.generate_readme")
@patch("pipeline.main.evaluate_repo", new_callable=AsyncMock)
@patch("pipeline.main.filter_candidates")
@patch("pipeline.main.discover_candidates", new_callable=AsyncMock)
@patch("pipeline.main.load_tools")
@patch("pipeline.main.load_categories")
@patch("pipeline.main.load_sources")
@patch("pipeline.main.save_tools")
@patch("pipeline.main.get_llm_client")
async def test_run_pipeline_end_to_end(
    mock_llm_client, mock_save, mock_load_sources, mock_load_cats,
    mock_load_tools, mock_discover, mock_filter, mock_evaluate,
    mock_generate, mock_create_pr,
):
    # Setup
    mock_load_tools.return_value = []
    mock_load_cats.return_value = [{"id": "search", "name": "Search", "description": "Search"}]
    mock_load_sources.return_value = {"scoring": {"min_stars": 50, "min_quality_score": 6, "max_inactive_days": 180}, "sources": {}}

    repo = GitHubRepo(
        full_name="owner/tool",
        url="https://github.com/owner/tool",
        description="A tool",
        stars=1000,
        language="Rust",
        license="MIT",
        pushed_at="2026-03-01T00:00:00Z",
        topics=["cli"],
    )
    mock_discover.return_value = [repo]
    mock_filter.return_value = [ScoredRepo(repo=repo, score=80.0)]
    mock_evaluate.return_value = EvalResult(
        accepted=True, quality_score=8, category="search",
        description="A great tool", reasoning="Good",
    )
    mock_generate.return_value = "# README"
    mock_create_pr.return_value = "https://github.com/owner/repo/pull/1"
    mock_llm_client.return_value = MagicMock()

    result = await run_pipeline(dry_run=True)
    assert result["discovered"] == 1
    assert result["scored"] == 1
    assert result["accepted"] == 1
