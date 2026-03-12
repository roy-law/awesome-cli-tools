# tests/test_generate.py
from pathlib import Path

import pytest

from pipeline.generate import generate_readme, format_stars


def test_format_stars():
    assert format_stars(48000) == "48k"
    assert format_stars(1500) == "1.5k"
    assert format_stars(500) == "500"
    assert format_stars(999) == "999"
    assert format_stars(1000) == "1k"


def test_generate_readme_empty(tmp_path: Path):
    categories = [{"id": "search", "name": "Search & Grep", "description": "Search tools"}]
    result = generate_readme(tools=[], categories=categories)
    assert "# Awesome CLI Tools" in result
    assert "Search & Grep" not in result  # no tools in category = section hidden


def test_generate_readme_with_tools(tmp_path: Path):
    categories = [{"id": "search", "name": "Search & Grep", "description": "Search tools"}]
    tools = [
        {
            "name": "ripgrep",
            "url": "https://github.com/BurntSushi/ripgrep",
            "description": "Fast grep alternative",
            "category": "search",
            "language": "Rust",
            "license": "MIT",
            "stars": 48000,
        }
    ]
    result = generate_readme(tools=tools, categories=categories)
    assert "ripgrep" in result
    assert "48k" in result
    assert "Search & Grep" in result
