from datetime import datetime, timedelta, UTC

import pytest

from pipeline.score import score_repo, filter_candidates, ScoredRepo
from pipeline.sources.github_topics import GitHubRepo


def _make_repo(
    stars: int = 1000,
    pushed_days_ago: int = 10,
    archived: bool = False,
    fork: bool = False,
) -> GitHubRepo:
    pushed = (datetime.now(UTC) - timedelta(days=pushed_days_ago)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    return GitHubRepo(
        full_name="owner/tool",
        url="https://github.com/owner/tool",
        description="A tool",
        stars=stars,
        language="Rust",
        license="MIT",
        pushed_at=pushed,
        topics=["cli"],
    )


def test_score_repo_basic():
    repo = _make_repo(stars=5000, pushed_days_ago=5)
    scored = score_repo(repo)
    assert scored.score > 0
    assert scored.repo == repo


def test_score_repo_higher_stars_higher_score():
    low = score_repo(_make_repo(stars=100))
    high = score_repo(_make_repo(stars=10000))
    assert high.score > low.score


def test_score_repo_stale_gets_penalty():
    fresh = score_repo(_make_repo(pushed_days_ago=5))
    stale = score_repo(_make_repo(pushed_days_ago=170))
    assert fresh.score > stale.score


def test_filter_rejects_below_min_stars():
    repo = _make_repo(stars=10)
    candidates = filter_candidates([repo], min_stars=50)
    assert len(candidates) == 0


def test_filter_rejects_inactive():
    repo = _make_repo(pushed_days_ago=200)
    candidates = filter_candidates([repo], max_inactive_days=180)
    assert len(candidates) == 0


def test_filter_keeps_good_repos():
    repo = _make_repo(stars=500, pushed_days_ago=10)
    candidates = filter_candidates([repo], min_stars=50, max_inactive_days=180)
    assert len(candidates) == 1
