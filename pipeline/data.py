"""Data loading and saving utilities for tools, categories, and sources."""

from pathlib import Path
from typing import Any

import yaml

Tool = dict[str, Any]

DATA_DIR = Path(__file__).parent.parent / "data"


def load_tools(path: Path | None = None) -> list[Tool]:
    path = path or DATA_DIR / "tools.yaml"
    with open(path) as f:
        data = yaml.safe_load(f)
    return data if data else []


def save_tools(tools: list[Tool], path: Path | None = None) -> None:
    path = path or DATA_DIR / "tools.yaml"
    with open(path, "w") as f:
        yaml.dump(tools, f, default_flow_style=False, sort_keys=False)


def load_categories(path: Path | None = None) -> list[dict]:
    path = path or DATA_DIR / "categories.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


def load_sources(path: Path | None = None) -> dict:
    path = path or DATA_DIR / "sources.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


def existing_repos(path: Path | None = None) -> set[str]:
    """Return set of repo slugs (owner/name) already in tools.yaml."""
    tools = load_tools(path)
    return {t["repo"] for t in tools}
