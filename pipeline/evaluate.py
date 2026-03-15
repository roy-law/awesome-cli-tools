"""Gate 2: AI editorial evaluation of candidate repos."""

import json
import os
from dataclasses import dataclass

import httpx

from pipeline.llm import LLMClient
from pipeline.score import ScoredRepo

EVAL_SYSTEM = """You are a curator for an awesome-list of CLI and TUI tools.
Evaluate whether a GitHub repository is a genuine, high-quality CLI/TUI tool
worth including in a curated list. You will be given the repo's README content
to make an informed judgment.

Respond with valid JSON only, no markdown fencing."""

EVAL_PROMPT = """Evaluate this repository:

Name: {name}
URL: {url}
Description: {description}
Language: {language}
Stars: {stars}
License: {license}
Topics: {topics}

README (first 3000 chars):
{readme}

Already listed tools (avoid duplicates):
{existing}

Available categories: {categories}

Respond with this exact JSON structure:
{{
  "is_cli_tool": true/false,
  "quality_score": 1-10,
  "category": "category-id",
  "description": "One-line description for the list (max 100 chars)",
  "reasoning": "Brief explanation of your judgment"
}}"""


@dataclass
class EvalResult:
    accepted: bool
    quality_score: int
    category: str
    description: str
    reasoning: str


async def fetch_readme(repo_full_name: str) -> str:
    """Fetch a repo's README content via the GitHub API."""
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"Accept": "application/vnd.github.raw+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(headers=headers, timeout=15) as client:
        response = await client.get(
            f"https://api.github.com/repos/{repo_full_name}/readme",
        )
        if response.status_code == 200:
            return response.text[:3000]
        return "(README not available)"


async def evaluate_repo(
    scored: ScoredRepo,
    existing_descriptions: list[str],
    categories: list[str],
    llm: LLMClient,
    min_quality: int = 6,
    readme: str | None = None,
) -> EvalResult:
    """Ask the LLM to evaluate a single repo."""
    repo = scored.repo

    if readme is None:
        readme = await fetch_readme(repo.full_name)

    prompt = EVAL_PROMPT.format(
        name=repo.full_name,
        url=repo.url,
        description=repo.description,
        language=repo.language or "Unknown",
        stars=repo.stars,
        license=repo.license or "Unknown",
        topics=", ".join(repo.topics),
        readme=readme,
        existing="\n".join(existing_descriptions[:50]) if existing_descriptions else "(none yet)",
        categories=", ".join(categories),
    )

    raw = await llm.complete(prompt, system=EVAL_SYSTEM)

    # Strip markdown fencing if present
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0]
    raw = raw.strip()

    data = json.loads(raw)

    is_cli = data.get("is_cli_tool", False)
    quality = data.get("quality_score", 0)
    accepted = is_cli and quality >= min_quality

    return EvalResult(
        accepted=accepted,
        quality_score=quality,
        category=data.get("category", "misc"),
        description=data.get("description", ""),
        reasoning=data.get("reasoning", ""),
    )
