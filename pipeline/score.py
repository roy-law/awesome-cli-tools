"""Gate 1: Algorithmic scoring and filtering of candidate repos."""

import math
from dataclasses import dataclass
from datetime import datetime, timedelta

from pipeline.sources.github_topics import GitHubRepo


@dataclass
class ScoredRepo:
    repo: GitHubRepo
    score: float
    trending: bool = False


def score_repo(repo: GitHubRepo) -> ScoredRepo:
    """Compute a quality score for a repo based on stars and activity."""
    star_score = math.log10(max(repo.stars, 1)) * 20

    try:
        pushed = datetime.fromisoformat(repo.pushed_at.replace("Z", "+00:00"))
        days_since = (datetime.now(pushed.tzinfo) - pushed).days
    except (ValueError, AttributeError):
        days_since = 365

    freshness_score = max(0, 30 - (days_since / 6))

    desc_score = 10 if repo.description and len(repo.description) > 20 else 0

    license_score = 5 if repo.license else 0

    total = star_score + freshness_score + desc_score + license_score
    return ScoredRepo(repo=repo, score=round(total, 2))


def filter_candidates(
    repos: list[GitHubRepo],
    min_stars: int = 50,
    max_inactive_days: int = 180,
) -> list[ScoredRepo]:
    """Filter and score repos, rejecting those below thresholds."""
    now = datetime.utcnow()
    cutoff = now - timedelta(days=max_inactive_days)
    results: list[ScoredRepo] = []

    for repo in repos:
        if repo.stars < min_stars:
            continue

        try:
            pushed = datetime.fromisoformat(repo.pushed_at.replace("Z", "+00:00"))
            if pushed.replace(tzinfo=None) < cutoff:
                continue
        except (ValueError, AttributeError):
            continue

        results.append(score_repo(repo))

    results.sort(key=lambda s: s.score, reverse=True)
    return results
