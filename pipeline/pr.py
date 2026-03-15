"""Gate 3: Create a GitHub PR with proposed tool additions."""

import subprocess
from datetime import datetime, UTC

from pipeline.evaluate import EvalResult


def build_pr_body(tools: list[dict], evals: list[EvalResult]) -> str:
    """Build the PR description body."""
    lines = [
        f"## 🤖 Auto-discovery: {len(tools)} new tool(s)",
        "",
        f"Discovered on {datetime.now(UTC).strftime('%Y-%m-%d')} by the weekly pipeline.",
        "",
        "### Proposed additions",
        "",
    ]
    for tool, eval_result in zip(tools, evals):
        lines.append(f"#### [{tool['name']}]({tool['url']})")
        lines.append(f"- **Repo:** {tool['repo']}")
        lines.append(f"- **Category:** {eval_result.category}")
        lines.append(f"- **Quality: {eval_result.quality_score}/10**")
        lines.append(f"- **Stars:** {tool.get('stars', 'N/A')}")
        lines.append(f"- **Description:** {eval_result.description}")
        lines.append(f"- **Reasoning:** {eval_result.reasoning}")
        lines.append("")

    lines.append("---")
    lines.append("*This PR was created automatically by the awesome-cli-tools pipeline.*")
    return "\n".join(lines)


def create_pr(
    tools: list[dict],
    evals: list[EvalResult],
    branch_name: str | None = None,
    dry_run: bool = False,
) -> str | None:
    """Create a git branch, commit changes, push, and open a PR.

    Returns the PR URL, or None if dry_run.
    """
    date_str = datetime.now(UTC).strftime("%Y-%m-%d")
    branch_name = branch_name or f"auto-discover/{date_str}"
    title = f"🤖 Add {len(tools)} new CLI tool(s) — {date_str}"
    body = build_pr_body(tools, evals)

    if dry_run:
        print(f"[DRY RUN] Would create PR: {title}")
        print(f"[DRY RUN] Branch: {branch_name}")
        print(f"[DRY RUN] Body:\n{body}")
        return None

    # Create branch and commit
    subprocess.run(["git", "checkout", "-b", branch_name], check=True)
    subprocess.run(["git", "add", "data/tools.yaml", "README.md"], check=True)
    subprocess.run(
        ["git", "commit", "-m", f"feat: add {len(tools)} new CLI tool(s)"],
        check=True,
    )
    subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)

    # Create PR via gh CLI
    result = subprocess.run(
        ["gh", "pr", "create", "--title", title, "--body", body],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()
