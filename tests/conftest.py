from pathlib import Path

import pytest
import yaml


@pytest.fixture
def data_dir() -> Path:
    return Path(__file__).parent.parent / "data"


@pytest.fixture
def sample_tool() -> dict:
    return {
        "name": "ripgrep",
        "repo": "BurntSushi/ripgrep",
        "url": "https://github.com/BurntSushi/ripgrep",
        "description": "Fast recursive grep alternative written in Rust",
        "category": "search",
        "language": "Rust",
        "license": "MIT",
        "stars": 48000,
        "added_date": "2026-03-11",
        "discovered_by": "github_trending",
    }


@pytest.fixture
def sample_tools_yaml(tmp_path: Path, sample_tool: dict) -> Path:
    tools_file = tmp_path / "tools.yaml"
    tools_file.write_text(yaml.dump([sample_tool], default_flow_style=False))
    return tools_file
