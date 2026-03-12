"""Main pipeline orchestrator: discover -> score -> evaluate -> PR."""

import asyncio
from datetime import date
from pathlib import Path

from pipeline.data import (
    load_tools,
    save_tools,
    load_categories,
    load_sources,
    existing_repos,
    DATA_DIR,
)
from pipeline.discover import discover_candidates
from pipeline.evaluate import evaluate_repo
from pipeline.generate import generate_readme
from pipeline.llm import get_llm_client
from pipeline.pr import create_pr
from pipeline.score import filter_candidates


async def run_pipeline(dry_run: bool = False) -> dict:
    """Run the full discovery pipeline."""
    # Load current state
    tools = load_tools()
    categories = load_categories()
    sources_config = load_sources()
    scoring = sources_config.get("scoring", {})
    known_repos = existing_repos()

    print(f"Loaded {len(tools)} existing tools")

    # Gate 0: Discover
    candidates = await discover_candidates(
        existing_repos=known_repos,
        sources_config=sources_config,
    )
    print(f"Discovered {len(candidates)} new candidates")

    # Gate 1: Score & filter
    scored = filter_candidates(
        candidates,
        min_stars=scoring.get("min_stars", 50),
        max_inactive_days=scoring.get("max_inactive_days", 180),
    )
    print(f"{len(scored)} passed algorithmic scoring")

    if not scored:
        print("No candidates passed scoring. Done.")
        return {"discovered": len(candidates), "scored": 0, "accepted": 0}

    # Gate 2: AI evaluation
    llm = get_llm_client()
    category_ids = [c["id"] for c in categories]
    existing_descs = [t["description"] for t in tools]

    accepted_tools: list[dict] = []
    accepted_evals = []

    for s in scored:
        eval_result = await evaluate_repo(
            s,
            existing_descriptions=existing_descs,
            categories=category_ids,
            llm=llm,
            min_quality=scoring.get("min_quality_score", 6),
        )
        if eval_result.accepted:
            tool_entry = {
                "name": s.repo.full_name.split("/")[-1],
                "repo": s.repo.full_name,
                "url": s.repo.url,
                "description": eval_result.description,
                "category": eval_result.category,
                "language": s.repo.language or "Unknown",
                "license": s.repo.license or "Unknown",
                "stars": s.repo.stars,
                "added_date": str(date.today()),
                "discovered_by": "pipeline",
            }
            accepted_tools.append(tool_entry)
            accepted_evals.append(eval_result)

    print(f"{len(accepted_tools)} passed AI evaluation")

    if not accepted_tools:
        print("No candidates passed AI evaluation. Done.")
        return {"discovered": len(candidates), "scored": len(scored), "accepted": 0}

    # Update data
    new_tools = tools + accepted_tools
    save_tools(new_tools)

    # Regenerate README
    readme_content = generate_readme(new_tools, categories)
    readme_path = Path(__file__).parent.parent / "README.md"
    readme_path.write_text(readme_content)

    # Gate 3: Create PR
    pr_url = create_pr(accepted_tools, accepted_evals, dry_run=dry_run)
    if pr_url:
        print(f"PR created: {pr_url}")

    return {
        "discovered": len(candidates),
        "scored": len(scored),
        "accepted": len(accepted_tools),
        "pr_url": pr_url,
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run the awesome-cli-tools discovery pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Don't create PR, just print results")
    args = parser.parse_args()
    result = asyncio.run(run_pipeline(dry_run=args.dry_run))
    print(f"\nPipeline complete: {result}")


if __name__ == "__main__":
    main()
