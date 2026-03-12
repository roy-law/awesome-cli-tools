"""Render tools YAML data into a formatted README.md using Jinja2."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def format_stars(stars: int) -> str:
    if stars >= 1000:
        val = stars / 1000
        if val == int(val):
            return f"{int(val)}k"
        return f"{val:.1f}k"
    return str(stars)


def generate_readme(
    tools: list[dict],
    categories: list[dict],
    templates_dir: Path | None = None,
) -> str:
    """Generate README markdown from tools and categories."""
    templates_dir = templates_dir or TEMPLATES_DIR

    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        keep_trailing_newline=True,
    )
    template = env.get_template("readme.md.jinja")

    # Add formatted stars to each tool
    for tool in tools:
        tool["stars_display"] = format_stars(tool.get("stars", 0))

    # Group tools by category
    tools_by_category: dict[str, list[dict]] = {}
    for tool in sorted(tools, key=lambda t: t.get("stars", 0), reverse=True):
        cat = tool.get("category", "misc")
        tools_by_category.setdefault(cat, []).append(tool)

    return template.render(
        categories=categories,
        tools_by_category=tools_by_category,
    )
