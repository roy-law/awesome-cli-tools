from pathlib import Path

import yaml

from pipeline.data import load_tools, save_tools, load_categories, load_sources, Tool


def test_load_tools_empty(tmp_path: Path):
    tools_file = tmp_path / "tools.yaml"
    tools_file.write_text("[]")
    tools = load_tools(tools_file)
    assert tools == []


def test_load_tools_with_entry(sample_tools_yaml: Path):
    tools = load_tools(sample_tools_yaml)
    assert len(tools) == 1
    assert tools[0]["name"] == "ripgrep"


def test_save_tools_roundtrip(tmp_path: Path, sample_tool: dict):
    tools_file = tmp_path / "tools.yaml"
    save_tools([sample_tool], tools_file)
    loaded = load_tools(tools_file)
    assert loaded == [sample_tool]


def test_load_categories(data_dir: Path):
    categories = load_categories(data_dir / "categories.yaml")
    assert len(categories) > 0
    assert categories[0]["id"] == "search"


def test_load_sources(data_dir: Path):
    sources = load_sources(data_dir / "sources.yaml")
    assert "scoring" in sources
    assert "sources" in sources
    assert sources["scoring"]["min_stars"] == 50


def test_tool_already_listed(sample_tools_yaml: Path):
    tools = load_tools(sample_tools_yaml)
    repos = {t["repo"] for t in tools}
    assert "BurntSushi/ripgrep" in repos
    assert "nonexistent/repo" not in repos
