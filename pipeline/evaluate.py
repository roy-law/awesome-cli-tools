"""Gate 2: AI editorial evaluation of candidate repos."""

import json
from dataclasses import dataclass

from pipeline.llm import LLMClient
from pipeline.score import ScoredRepo

EVAL_SYSTEM = """You are a curator for an awesome-list of CLI and TUI tools.
Evaluate whether a GitHub repository is a genuine, high-quality CLI/TUI tool
worth including in a curated list.

Respond with valid JSON only, no markdown fencing."""

EVAL_PROMPT = """Evaluate this repository:

Name: {name}
URL: {url}
Description: {description}
Language: {language}
Stars: {stars}
License: {license}
Topics: {topics}

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


async def evaluate_repo(
    scored: ScoredRepo,
    existing_descriptions: list[str],
    categories: list[str],
    llm: LLMClient,
    min_quality: int = 6,
) -> EvalResult:
    """Ask the LLM to evaluate a single repo."""
    repo = scored.repo
    prompt = EVAL_PROMPT.format(
        name=repo.full_name,
        url=repo.url,
        description=repo.description,
        language=repo.language or "Unknown",
        stars=repo.stars,
        license=repo.license or "Unknown",
        topics=", ".join(repo.topics),
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
