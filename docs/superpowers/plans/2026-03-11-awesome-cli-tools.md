# awesome-cli-tools Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a self-improving GitHub repo that automatically discovers, scores, and curates CLI tools using AI, opening weekly PRs with proposed additions.

**Architecture:** YAML-as-source-of-truth with a 4-gate pipeline (discover → score → evaluate → PR). Python scripts run via GitHub Actions weekly cron. LLM provider is configurable via env vars.

**Tech Stack:** Python 3.12+, httpx, PyYAML, Jinja2, anthropic/openai SDKs, pytest, GitHub Actions

**Spec:** `docs/superpowers/specs/2026-03-11-awesome-cli-tools-design.md`

---

## Chunk 1: Project Scaffolding & Data Layer

### Task 1: Project scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `LICENSE`
- Create: `CONTRIBUTING.md`
- Create: `pipeline/__init__.py`
- Create: `pipeline/sources/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "awesome-cli-tools"
version = "0.1.0"
description = "AI-curated list of awesome CLI tools"
requires-python = ">=3.12"
dependencies = [
    "httpx>=0.27",
    "pyyaml>=6.0",
    "jinja2>=3.1",
    "anthropic>=0.40",
    "openai>=1.50",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "respx>=0.22",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

- [ ] **Step 2: Create .gitignore**

```
__pycache__/
*.pyc
.venv/
.env
dist/
*.egg-info/
.pytest_cache/
```

- [ ] **Step 3: Create LICENSE (MIT)**

Standard MIT license with year 2026.

- [ ] **Step 4: Create CONTRIBUTING.md**

```markdown
# Contributing

## How This Repo Works

This list is **AI-curated**. A weekly pipeline discovers trending CLI tools, scores them, and opens PRs with proposed additions.

## Manual Submissions

You can also submit tools manually by opening a PR that adds an entry to `data/tools.yaml`.

### Entry format

```yaml
- name: tool-name
  repo: owner/repo
  url: https://github.com/owner/repo
  description: "One-line description"
  category: category-name
  language: Language
  license: MIT
```

Categories are defined in `data/categories.yaml`.

## Running the Pipeline Locally

```bash
pip install -e ".[dev]"
python -m pipeline.discover    # Find candidates
python -m pipeline.score       # Score them
python -m pipeline.evaluate    # AI evaluation
python -m pipeline.generate    # Rebuild README
```
```

- [ ] **Step 5: Create package init files**

Create empty `pipeline/__init__.py`, `pipeline/sources/__init__.py`, `tests/__init__.py`.

- [ ] **Step 6: Create tests/conftest.py**

```python
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
```

- [ ] **Step 7: Commit scaffolding**

```bash
git add pyproject.toml .gitignore LICENSE CONTRIBUTING.md pipeline/__init__.py pipeline/sources/__init__.py tests/__init__.py tests/conftest.py
git commit -m "feat: project scaffolding with pyproject.toml and test fixtures"
```

---

### Task 2: Data files — categories and sources config

**Files:**
- Create: `data/categories.yaml`
- Create: `data/sources.yaml`
- Create: `data/tools.yaml`

- [ ] **Step 1: Create data/categories.yaml**

```yaml
- id: search
  name: Search & Grep
  description: Tools for searching files, text, and code

- id: file-management
  name: File Management
  description: File managers, directory tools, and file operations

- id: shell
  name: Shell & Terminal
  description: Shell frameworks, terminal emulators, and prompt customization

- id: git
  name: Git & Version Control
  description: Git utilities, diff tools, and repository management

- id: text-processing
  name: Text Processing
  description: Text manipulation, formatting, and conversion tools

- id: networking
  name: Networking
  description: HTTP clients, network diagnostics, and API tools

- id: system
  name: System & Monitoring
  description: System info, process management, and monitoring

- id: dev-tools
  name: Development Tools
  description: Build tools, linters, formatters, and development utilities

- id: productivity
  name: Productivity
  description: Task management, notes, time tracking, and workflow tools

- id: data
  name: Data & JSON
  description: JSON/CSV/YAML processing and data manipulation

- id: media
  name: Media & Images
  description: Image, video, and audio tools for the terminal

- id: security
  name: Security
  description: Security scanning, encryption, and password management

- id: containers
  name: Containers & Cloud
  description: Docker, Kubernetes, and cloud CLI tools

- id: ai
  name: AI & LLM
  description: AI-powered CLI tools and LLM interfaces

- id: misc
  name: Miscellaneous
  description: Tools that don't fit other categories
```

- [ ] **Step 2: Create data/sources.yaml**

```yaml
scoring:
  min_stars: 50
  min_quality_score: 6
  trending_threshold: 500  # stars gained in 30 days
  max_inactive_days: 180

sources:
  github_topics:
    enabled: true
    topics:
      - cli
      - command-line
      - terminal
      - tui
      - command-line-tool
    per_topic_limit: 100

  github_trending:
    enabled: true
    languages:
      - ""        # all languages
      - rust
      - go
      - python
      - typescript

  hackernews:
    enabled: false  # phase 2
    min_points: 50

  reddit:
    enabled: false  # phase 2
    subreddits:
      - commandline
      - cli
      - terminal

  awesome_lists:
    enabled: false  # phase 2
    lists:
      - alebcay/awesome-shell
      - agarrharr/awesome-cli-apps
```

- [ ] **Step 3: Create data/tools.yaml (empty seed)**

```yaml
# Awesome CLI Tools — Source of Truth
# This file is managed by the discovery pipeline.
# Manual additions welcome via PR.
[]
```

- [ ] **Step 4: Commit data files**

```bash
git add data/
git commit -m "feat: add category definitions, source config, and empty tools seed"
```

---

### Task 3: Data loading utilities

**Files:**
- Create: `pipeline/data.py`
- Create: `tests/test_data.py`

- [ ] **Step 1: Write failing tests for data loading**

```python
# tests/test_data.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/roy/Documents/Github/awesome-cli-tools && python -m pytest tests/test_data.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'pipeline.data'`

- [ ] **Step 3: Implement pipeline/data.py**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/roy/Documents/Github/awesome-cli-tools && python -m pytest tests/test_data.py -v`
Expected: All 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add pipeline/data.py tests/test_data.py
git commit -m "feat: data loading utilities for tools, categories, and sources"
```

---

## Chunk 2: LLM Abstraction & Discovery Sources

### Task 4: LLM abstraction layer

**Files:**
- Create: `pipeline/llm.py`
- Create: `tests/test_llm.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_llm.py
import os
from unittest.mock import patch, MagicMock, AsyncMock

import pytest

from pipeline.llm import get_llm_client, LLMClient


def test_get_llm_client_anthropic():
    with patch.dict(os.environ, {"LLM_PROVIDER": "anthropic", "LLM_MODEL": "claude-haiku-4-5-20251001"}):
        client = get_llm_client()
        assert client.provider == "anthropic"
        assert client.model == "claude-haiku-4-5-20251001"


def test_get_llm_client_openai():
    with patch.dict(os.environ, {"LLM_PROVIDER": "openai", "LLM_MODEL": "gpt-4o-mini"}):
        client = get_llm_client()
        assert client.provider == "openai"
        assert client.model == "gpt-4o-mini"


def test_get_llm_client_defaults():
    with patch.dict(os.environ, {}, clear=True):
        env = {k: v for k, v in os.environ.items()}
        # Remove LLM vars if present
        env.pop("LLM_PROVIDER", None)
        env.pop("LLM_MODEL", None)
        with patch.dict(os.environ, env, clear=True):
            client = get_llm_client()
            assert client.provider == "anthropic"
            assert client.model == "claude-haiku-4-5-20251001"


@pytest.mark.asyncio
async def test_llm_client_complete_anthropic():
    mock_anthropic = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="test response")]
    mock_anthropic.messages.create = AsyncMock(return_value=mock_response)

    client = LLMClient(provider="anthropic", model="claude-haiku-4-5-20251001")
    with patch.object(client, "_anthropic_client", mock_anthropic):
        result = await client.complete("test prompt", system="you are helpful")
        assert result == "test response"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_llm.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement pipeline/llm.py**

```python
"""Configurable LLM abstraction layer supporting Anthropic and OpenAI."""

import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMClient:
    provider: str = "anthropic"
    model: str = "claude-haiku-4-5-20251001"
    _anthropic_client: Any = field(default=None, repr=False)
    _openai_client: Any = field(default=None, repr=False)

    def _get_anthropic(self):
        if self._anthropic_client is None:
            import anthropic
            self._anthropic_client = anthropic.AsyncAnthropic()
        return self._anthropic_client

    def _get_openai(self):
        if self._openai_client is None:
            import openai
            self._openai_client = openai.AsyncOpenAI()
        return self._openai_client

    async def complete(self, prompt: str, system: str = "") -> str:
        if self.provider == "anthropic":
            client = self._get_anthropic()
            response = await client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        elif self.provider == "openai":
            client = self._get_openai()
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            return response.choices[0].message.content
        else:
            raise ValueError(f"Unknown provider: {self.provider}")


def get_llm_client() -> LLMClient:
    provider = os.environ.get("LLM_PROVIDER", "anthropic")
    model = os.environ.get("LLM_MODEL", "claude-haiku-4-5-20251001")
    return LLMClient(provider=provider, model=model)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_llm.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add pipeline/llm.py tests/test_llm.py
git commit -m "feat: configurable LLM abstraction supporting Anthropic and OpenAI"
```

---

### Task 5: GitHub Topics discovery source

**Files:**
- Create: `pipeline/sources/github_topics.py`
- Create: `tests/test_github_topics.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_github_topics.py
import httpx
import pytest
import respx

from pipeline.sources.github_topics import search_github_topics, GitHubRepo


@respx.mock
@pytest.mark.asyncio
async def test_search_github_topics_parses_response():
    mock_response = {
        "items": [
            {
                "full_name": "BurntSushi/ripgrep",
                "html_url": "https://github.com/BurntSushi/ripgrep",
                "description": "ripgrep recursively searches directories",
                "stargazers_count": 48000,
                "fork": False,
                "archived": False,
                "language": "Rust",
                "license": {"spdx_id": "MIT"},
                "pushed_at": "2026-03-01T00:00:00Z",
                "topics": ["cli", "grep", "search"],
            }
        ]
    }
    respx.get("https://api.github.com/search/repositories").mock(
        return_value=httpx.Response(200, json=mock_response)
    )
    repos = await search_github_topics(topics=["cli"], per_topic_limit=10)
    assert len(repos) == 1
    assert repos[0].full_name == "BurntSushi/ripgrep"
    assert repos[0].stars == 48000


@respx.mock
@pytest.mark.asyncio
async def test_search_github_topics_skips_forks():
    mock_response = {
        "items": [
            {
                "full_name": "fork/ripgrep",
                "html_url": "https://github.com/fork/ripgrep",
                "description": "A fork",
                "stargazers_count": 100,
                "fork": True,
                "archived": False,
                "language": "Rust",
                "license": None,
                "pushed_at": "2026-03-01T00:00:00Z",
                "topics": [],
            }
        ]
    }
    respx.get("https://api.github.com/search/repositories").mock(
        return_value=httpx.Response(200, json=mock_response)
    )
    repos = await search_github_topics(topics=["cli"], per_topic_limit=10)
    assert len(repos) == 0


@respx.mock
@pytest.mark.asyncio
async def test_search_github_topics_deduplicates():
    item = {
        "full_name": "BurntSushi/ripgrep",
        "html_url": "https://github.com/BurntSushi/ripgrep",
        "description": "ripgrep",
        "stargazers_count": 48000,
        "fork": False,
        "archived": False,
        "language": "Rust",
        "license": {"spdx_id": "MIT"},
        "pushed_at": "2026-03-01T00:00:00Z",
        "topics": ["cli"],
    }
    # Same repo returned for multiple topic queries
    respx.get("https://api.github.com/search/repositories").mock(
        return_value=httpx.Response(200, json={"items": [item]})
    )
    repos = await search_github_topics(topics=["cli", "terminal"], per_topic_limit=10)
    assert len(repos) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_github_topics.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement pipeline/sources/github_topics.py**

```python
"""Discover CLI tools by searching GitHub topics."""

import os
from dataclasses import dataclass

import httpx


@dataclass
class GitHubRepo:
    full_name: str
    url: str
    description: str
    stars: int
    language: str | None
    license: str | None
    pushed_at: str
    topics: list[str]


async def search_github_topics(
    topics: list[str],
    per_topic_limit: int = 100,
) -> list[GitHubRepo]:
    """Search GitHub for repos matching given topics, deduplicated."""
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    seen: set[str] = set()
    repos: list[GitHubRepo] = []

    async with httpx.AsyncClient(headers=headers, timeout=30) as client:
        for topic in topics:
            params = {
                "q": f"topic:{topic}",
                "sort": "stars",
                "order": "desc",
                "per_page": min(per_topic_limit, 100),
            }
            response = await client.get(
                "https://api.github.com/search/repositories",
                params=params,
            )
            response.raise_for_status()
            data = response.json()

            for item in data.get("items", []):
                if item["fork"] or item["archived"]:
                    continue
                if item["full_name"] in seen:
                    continue
                seen.add(item["full_name"])

                license_id = None
                if item.get("license"):
                    license_id = item["license"].get("spdx_id")

                repos.append(
                    GitHubRepo(
                        full_name=item["full_name"],
                        url=item["html_url"],
                        description=item.get("description") or "",
                        stars=item["stargazers_count"],
                        language=item.get("language"),
                        license=license_id,
                        pushed_at=item["pushed_at"],
                        topics=item.get("topics", []),
                    )
                )

    return repos
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_github_topics.py -v`
Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add pipeline/sources/github_topics.py tests/test_github_topics.py
git commit -m "feat: GitHub topics discovery source with dedup and fork filtering"
```

---

### Task 6: GitHub Trending discovery source

**Files:**
- Create: `pipeline/sources/github_trending.py`
- Create: `tests/test_github_trending.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_github_trending.py
import httpx
import pytest
import respx

from pipeline.sources.github_trending import search_github_trending, GitHubRepo


@respx.mock
@pytest.mark.asyncio
async def test_search_trending_uses_created_filter():
    """Trending = recently created repos with high stars, queried via search API."""
    respx.get("https://api.github.com/search/repositories").mock(
        return_value=httpx.Response(200, json={"items": []})
    )
    await search_github_trending(languages=["rust"])
    call = respx.calls[0]
    query = str(call.request.url)
    assert "created" in query  # should filter by recent creation date


@respx.mock
@pytest.mark.asyncio
async def test_search_trending_parses_repos():
    mock_response = {
        "items": [
            {
                "full_name": "astral-sh/uv",
                "html_url": "https://github.com/astral-sh/uv",
                "description": "Fast Python package manager",
                "stargazers_count": 30000,
                "fork": False,
                "archived": False,
                "language": "Rust",
                "license": {"spdx_id": "MIT"},
                "pushed_at": "2026-03-10T00:00:00Z",
                "topics": ["python", "package-manager"],
            }
        ]
    }
    respx.get("https://api.github.com/search/repositories").mock(
        return_value=httpx.Response(200, json=mock_response)
    )
    repos = await search_github_trending(languages=["rust"])
    assert len(repos) == 1
    assert repos[0].full_name == "astral-sh/uv"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_github_trending.py -v`
Expected: FAIL

- [ ] **Step 3: Implement pipeline/sources/github_trending.py**

```python
"""Discover trending CLI-related repos on GitHub using the search API."""

import os
from datetime import datetime, timedelta

import httpx

from pipeline.sources.github_topics import GitHubRepo


async def search_github_trending(
    languages: list[str] | None = None,
    days: int = 30,
    per_page: int = 50,
) -> list[GitHubRepo]:
    """Find repos created in the last N days with high star counts."""
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    languages = languages or [""]
    seen: set[str] = set()
    repos: list[GitHubRepo] = []

    async with httpx.AsyncClient(headers=headers, timeout=30) as client:
        for lang in languages:
            q = f"created:>{since} stars:>50"
            if lang:
                q += f" language:{lang}"

            params = {
                "q": q,
                "sort": "stars",
                "order": "desc",
                "per_page": per_page,
            }
            response = await client.get(
                "https://api.github.com/search/repositories",
                params=params,
            )
            response.raise_for_status()

            for item in response.json().get("items", []):
                if item["fork"] or item["archived"]:
                    continue
                if item["full_name"] in seen:
                    continue
                seen.add(item["full_name"])

                license_id = None
                if item.get("license"):
                    license_id = item["license"].get("spdx_id")

                repos.append(
                    GitHubRepo(
                        full_name=item["full_name"],
                        url=item["html_url"],
                        description=item.get("description") or "",
                        stars=item["stargazers_count"],
                        language=item.get("language"),
                        license=license_id,
                        pushed_at=item["pushed_at"],
                        topics=item.get("topics", []),
                    )
                )

    return repos
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_github_trending.py -v`
Expected: All 2 tests PASS

- [ ] **Step 5: Commit**

```bash
git add pipeline/sources/github_trending.py tests/test_github_trending.py
git commit -m "feat: GitHub trending discovery source using search API"
```

---

### Task 7: Discover orchestrator

**Files:**
- Create: `pipeline/discover.py`
- Create: `tests/test_discover.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_discover.py
from unittest.mock import AsyncMock, patch

import pytest

from pipeline.discover import discover_candidates
from pipeline.sources.github_topics import GitHubRepo


def _make_repo(name: str, stars: int = 1000) -> GitHubRepo:
    return GitHubRepo(
        full_name=name,
        url=f"https://github.com/{name}",
        description=f"Description of {name}",
        stars=stars,
        language="Rust",
        license="MIT",
        pushed_at="2026-03-01T00:00:00Z",
        topics=["cli"],
    )


@pytest.mark.asyncio
@patch("pipeline.discover.search_github_topics", new_callable=AsyncMock)
@patch("pipeline.discover.search_github_trending", new_callable=AsyncMock)
async def test_discover_merges_sources(mock_trending, mock_topics):
    mock_topics.return_value = [_make_repo("owner/tool-a")]
    mock_trending.return_value = [_make_repo("owner/tool-b")]
    candidates = await discover_candidates(existing_repos=set())
    names = {c.full_name for c in candidates}
    assert "owner/tool-a" in names
    assert "owner/tool-b" in names


@pytest.mark.asyncio
@patch("pipeline.discover.search_github_topics", new_callable=AsyncMock)
@patch("pipeline.discover.search_github_trending", new_callable=AsyncMock)
async def test_discover_excludes_existing(mock_trending, mock_topics):
    mock_topics.return_value = [_make_repo("owner/existing")]
    mock_trending.return_value = []
    candidates = await discover_candidates(existing_repos={"owner/existing"})
    assert len(candidates) == 0


@pytest.mark.asyncio
@patch("pipeline.discover.search_github_topics", new_callable=AsyncMock)
@patch("pipeline.discover.search_github_trending", new_callable=AsyncMock)
async def test_discover_deduplicates_across_sources(mock_trending, mock_topics):
    repo = _make_repo("owner/tool-a")
    mock_topics.return_value = [repo]
    mock_trending.return_value = [repo]
    candidates = await discover_candidates(existing_repos=set())
    assert len(candidates) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_discover.py -v`
Expected: FAIL

- [ ] **Step 3: Implement pipeline/discover.py**

```python
"""Gate 0: Discover candidate CLI tools from multiple sources."""

from pipeline.data import load_sources
from pipeline.sources.github_topics import GitHubRepo, search_github_topics
from pipeline.sources.github_trending import search_github_trending


async def discover_candidates(
    existing_repos: set[str] | None = None,
    sources_config: dict | None = None,
) -> list[GitHubRepo]:
    """Fetch candidates from all enabled sources, dedup against existing tools."""
    if existing_repos is None:
        existing_repos = set()
    if sources_config is None:
        sources_config = load_sources()

    seen: set[str] = set(existing_repos)
    candidates: list[GitHubRepo] = []

    src = sources_config.get("sources", {})

    # GitHub Topics
    topics_cfg = src.get("github_topics", {})
    if topics_cfg.get("enabled", False):
        repos = await search_github_topics(
            topics=topics_cfg.get("topics", ["cli"]),
            per_topic_limit=topics_cfg.get("per_topic_limit", 100),
        )
        for repo in repos:
            if repo.full_name not in seen:
                seen.add(repo.full_name)
                candidates.append(repo)

    # GitHub Trending
    trending_cfg = src.get("github_trending", {})
    if trending_cfg.get("enabled", False):
        repos = await search_github_trending(
            languages=trending_cfg.get("languages", [""]),
        )
        for repo in repos:
            if repo.full_name not in seen:
                seen.add(repo.full_name)
                candidates.append(repo)

    # Future: hackernews, reddit, awesome_lists — add here when enabled

    return candidates
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_discover.py -v`
Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add pipeline/discover.py tests/test_discover.py
git commit -m "feat: discovery orchestrator merging multiple sources with dedup"
```

---

## Chunk 3: Scoring & AI Evaluation

### Task 8: Algorithmic scoring (Gate 1)

**Files:**
- Create: `pipeline/score.py`
- Create: `tests/test_score.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_score.py
from datetime import datetime, timedelta

import pytest

from pipeline.score import score_repo, filter_candidates, ScoredRepo
from pipeline.sources.github_topics import GitHubRepo


def _make_repo(
    stars: int = 1000,
    pushed_days_ago: int = 10,
    archived: bool = False,
    fork: bool = False,
) -> GitHubRepo:
    pushed = (datetime.utcnow() - timedelta(days=pushed_days_ago)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    return GitHubRepo(
        full_name="owner/tool",
        url="https://github.com/owner/tool",
        description="A tool",
        stars=stars,
        language="Rust",
        license="MIT",
        pushed_at=pushed,
        topics=["cli"],
    )


def test_score_repo_basic():
    repo = _make_repo(stars=5000, pushed_days_ago=5)
    scored = score_repo(repo)
    assert scored.score > 0
    assert scored.repo == repo


def test_score_repo_higher_stars_higher_score():
    low = score_repo(_make_repo(stars=100))
    high = score_repo(_make_repo(stars=10000))
    assert high.score > low.score


def test_score_repo_stale_gets_penalty():
    fresh = score_repo(_make_repo(pushed_days_ago=5))
    stale = score_repo(_make_repo(pushed_days_ago=170))
    assert fresh.score > stale.score


def test_filter_rejects_below_min_stars():
    repo = _make_repo(stars=10)
    candidates = filter_candidates([repo], min_stars=50)
    assert len(candidates) == 0


def test_filter_rejects_inactive():
    repo = _make_repo(pushed_days_ago=200)
    candidates = filter_candidates([repo], max_inactive_days=180)
    assert len(candidates) == 0


def test_filter_keeps_good_repos():
    repo = _make_repo(stars=500, pushed_days_ago=10)
    candidates = filter_candidates([repo], min_stars=50, max_inactive_days=180)
    assert len(candidates) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_score.py -v`
Expected: FAIL

- [ ] **Step 3: Implement pipeline/score.py**

```python
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
    # Star score: logarithmic to avoid mega-repos dominating
    star_score = math.log10(max(repo.stars, 1)) * 20

    # Freshness score: penalize repos with old last push
    try:
        pushed = datetime.fromisoformat(repo.pushed_at.replace("Z", "+00:00"))
        days_since = (datetime.now(pushed.tzinfo) - pushed).days
    except (ValueError, AttributeError):
        days_since = 365

    freshness_score = max(0, 30 - (days_since / 6))

    # Description quality: having a description is worth something
    desc_score = 10 if repo.description and len(repo.description) > 20 else 0

    # License: having one is a quality signal
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_score.py -v`
Expected: All 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add pipeline/score.py tests/test_score.py
git commit -m "feat: algorithmic scoring with star, freshness, and quality signals"
```

---

### Task 9: AI evaluation (Gate 2)

**Files:**
- Create: `pipeline/evaluate.py`
- Create: `tests/test_evaluate.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_evaluate.py
import json
from unittest.mock import AsyncMock, patch

import pytest

from pipeline.evaluate import evaluate_repo, EvalResult
from pipeline.score import ScoredRepo
from pipeline.sources.github_topics import GitHubRepo


def _make_scored_repo() -> ScoredRepo:
    repo = GitHubRepo(
        full_name="sharkdp/bat",
        url="https://github.com/sharkdp/bat",
        description="A cat clone with wings",
        stars=50000,
        language="Rust",
        license="MIT",
        pushed_at="2026-03-01T00:00:00Z",
        topics=["cli", "terminal"],
    )
    return ScoredRepo(repo=repo, score=85.0)


@pytest.mark.asyncio
async def test_evaluate_repo_accept():
    llm_response = json.dumps({
        "is_cli_tool": True,
        "quality_score": 9,
        "category": "file-management",
        "description": "A cat(1) clone with syntax highlighting and Git integration",
        "reasoning": "Well-known, high-quality CLI tool",
    })
    mock_llm = AsyncMock()
    mock_llm.complete = AsyncMock(return_value=llm_response)

    result = await evaluate_repo(
        _make_scored_repo(),
        existing_descriptions=[],
        categories=["search", "file-management", "shell"],
        llm=mock_llm,
    )
    assert result.accepted is True
    assert result.category == "file-management"
    assert result.quality_score == 9


@pytest.mark.asyncio
async def test_evaluate_repo_reject_low_quality():
    llm_response = json.dumps({
        "is_cli_tool": True,
        "quality_score": 3,
        "category": "misc",
        "description": "Some tool",
        "reasoning": "Low quality, poorly documented",
    })
    mock_llm = AsyncMock()
    mock_llm.complete = AsyncMock(return_value=llm_response)

    result = await evaluate_repo(
        _make_scored_repo(),
        existing_descriptions=[],
        categories=["misc"],
        llm=mock_llm,
    )
    assert result.accepted is False


@pytest.mark.asyncio
async def test_evaluate_repo_reject_not_cli():
    llm_response = json.dumps({
        "is_cli_tool": False,
        "quality_score": 8,
        "category": "misc",
        "description": "A web framework",
        "reasoning": "Not a CLI tool",
    })
    mock_llm = AsyncMock()
    mock_llm.complete = AsyncMock(return_value=llm_response)

    result = await evaluate_repo(
        _make_scored_repo(),
        existing_descriptions=[],
        categories=["misc"],
        llm=mock_llm,
    )
    assert result.accepted is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_evaluate.py -v`
Expected: FAIL

- [ ] **Step 3: Implement pipeline/evaluate.py**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_evaluate.py -v`
Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add pipeline/evaluate.py tests/test_evaluate.py
git commit -m "feat: AI evaluation gate with LLM-based quality and novelty scoring"
```

---

## Chunk 4: README Generation & PR Creation

### Task 10: README generation from YAML

**Files:**
- Create: `templates/readme.md.jinja`
- Create: `pipeline/generate.py`
- Create: `tests/test_generate.py`

- [ ] **Step 1: Create Jinja2 template**

```jinja2
{# templates/readme.md.jinja #}
# Awesome CLI Tools

> An AI-curated list of awesome command-line tools, automatically updated weekly.

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

This list is maintained by an automated pipeline that discovers trending CLI tools,
scores them algorithmically, and evaluates them with AI. [Learn how it works →](CONTRIBUTING.md)

## Contents
{% for cat in categories %}
- [{{ cat.name }}](#{{ cat.id }})
{%- endfor %}

---
{% for cat in categories %}
{% set cat_tools = tools_by_category.get(cat.id, []) %}
{% if cat_tools %}

## {{ cat.name }}

{{ cat.description }}

| Tool | Description | Language | License | Stars |
|------|-------------|----------|---------|-------|
{% for tool in cat_tools -%}
| [{{ tool.name }}]({{ tool.url }}) {{ "🔥" if tool.get("trending") else "" }} | {{ tool.description }} | `{{ tool.language }}` | `{{ tool.license }}` | {{ tool.stars_display }} |
{% endfor %}
{% endif %}
{%- endfor %}

---

## Legend

- 🔥 Trending — gained 500+ stars in the last month

## About

This list is automatically curated by an AI pipeline that runs weekly.
See [CONTRIBUTING.md](CONTRIBUTING.md) for how to submit tools manually.
```

- [ ] **Step 2: Write failing tests**

```python
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
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `python -m pytest tests/test_generate.py -v`
Expected: FAIL

- [ ] **Step 4: Implement pipeline/generate.py**

```python
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
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/test_generate.py -v`
Expected: All 3 tests PASS

- [ ] **Step 6: Commit**

```bash
git add templates/readme.md.jinja pipeline/generate.py tests/test_generate.py
git commit -m "feat: Jinja2-based README generation from YAML data"
```

---

### Task 11: PR creation (Gate 3)

**Files:**
- Create: `pipeline/pr.py`
- Create: `tests/test_pr.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_pr.py
from pipeline.pr import build_pr_body
from pipeline.evaluate import EvalResult


def test_build_pr_body_single_tool():
    tools = [
        {
            "name": "bat",
            "repo": "sharkdp/bat",
            "url": "https://github.com/sharkdp/bat",
            "description": "A cat clone with syntax highlighting",
            "category": "file-management",
            "stars": 50000,
        }
    ]
    evals = [
        EvalResult(
            accepted=True,
            quality_score=9,
            category="file-management",
            description="A cat clone with syntax highlighting",
            reasoning="High quality, well maintained",
        )
    ]
    body = build_pr_body(tools, evals)
    assert "bat" in body
    assert "sharkdp/bat" in body
    assert "Quality: 9/10" in body


def test_build_pr_body_multiple_tools():
    tools = [
        {"name": "bat", "repo": "sharkdp/bat", "url": "https://github.com/sharkdp/bat", "description": "Cat clone", "category": "file-management", "stars": 50000},
        {"name": "fd", "repo": "sharkdp/fd", "url": "https://github.com/sharkdp/fd", "description": "Find clone", "category": "search", "stars": 34000},
    ]
    evals = [
        EvalResult(accepted=True, quality_score=9, category="file-management", description="Cat clone", reasoning="Great"),
        EvalResult(accepted=True, quality_score=8, category="search", description="Find clone", reasoning="Good"),
    ]
    body = build_pr_body(tools, evals)
    assert "bat" in body
    assert "fd" in body
    assert "2 new tool(s)" in body
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_pr.py -v`
Expected: FAIL

- [ ] **Step 3: Implement pipeline/pr.py**

```python
"""Gate 3: Create a GitHub PR with proposed tool additions."""

import subprocess
from datetime import datetime

from pipeline.evaluate import EvalResult


def build_pr_body(tools: list[dict], evals: list[EvalResult]) -> str:
    """Build the PR description body."""
    lines = [
        f"## 🤖 Auto-discovery: {len(tools)} new tool(s)",
        "",
        f"Discovered on {datetime.utcnow().strftime('%Y-%m-%d')} by the weekly pipeline.",
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
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_pr.py -v`
Expected: All 2 tests PASS

- [ ] **Step 5: Commit**

```bash
git add pipeline/pr.py tests/test_pr.py
git commit -m "feat: PR creation with auto-generated description and git automation"
```

---

## Chunk 5: Main Pipeline & GitHub Actions

### Task 12: Main pipeline orchestrator

**Files:**
- Create: `pipeline/main.py`
- Create: `tests/test_main.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_main.py
from unittest.mock import AsyncMock, patch, MagicMock
import json

import pytest

from pipeline.main import run_pipeline
from pipeline.sources.github_topics import GitHubRepo
from pipeline.score import ScoredRepo
from pipeline.evaluate import EvalResult


@pytest.mark.asyncio
@patch("pipeline.main.create_pr")
@patch("pipeline.main.generate_readme")
@patch("pipeline.main.evaluate_repo", new_callable=AsyncMock)
@patch("pipeline.main.filter_candidates")
@patch("pipeline.main.discover_candidates", new_callable=AsyncMock)
@patch("pipeline.main.load_tools")
@patch("pipeline.main.load_categories")
@patch("pipeline.main.load_sources")
@patch("pipeline.main.save_tools")
@patch("pipeline.main.get_llm_client")
async def test_run_pipeline_end_to_end(
    mock_llm_client, mock_save, mock_load_sources, mock_load_cats,
    mock_load_tools, mock_discover, mock_filter, mock_evaluate,
    mock_generate, mock_create_pr,
):
    # Setup
    mock_load_tools.return_value = []
    mock_load_cats.return_value = [{"id": "search", "name": "Search", "description": "Search"}]
    mock_load_sources.return_value = {"scoring": {"min_stars": 50, "min_quality_score": 6, "max_inactive_days": 180}, "sources": {}}

    repo = GitHubRepo(
        full_name="owner/tool",
        url="https://github.com/owner/tool",
        description="A tool",
        stars=1000,
        language="Rust",
        license="MIT",
        pushed_at="2026-03-01T00:00:00Z",
        topics=["cli"],
    )
    mock_discover.return_value = [repo]
    mock_filter.return_value = [ScoredRepo(repo=repo, score=80.0)]
    mock_evaluate.return_value = EvalResult(
        accepted=True, quality_score=8, category="search",
        description="A great tool", reasoning="Good",
    )
    mock_generate.return_value = "# README"
    mock_create_pr.return_value = "https://github.com/owner/repo/pull/1"
    mock_llm_client.return_value = MagicMock()

    result = await run_pipeline(dry_run=True)
    assert result["discovered"] == 1
    assert result["scored"] == 1
    assert result["accepted"] == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_main.py -v`
Expected: FAIL

- [ ] **Step 3: Implement pipeline/main.py**

```python
"""Main pipeline orchestrator: discover → score → evaluate → PR."""

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

    print(f"📦 Loaded {len(tools)} existing tools")

    # Gate 0: Discover
    candidates = await discover_candidates(
        existing_repos=known_repos,
        sources_config=sources_config,
    )
    print(f"🔍 Discovered {len(candidates)} new candidates")

    # Gate 1: Score & filter
    scored = filter_candidates(
        candidates,
        min_stars=scoring.get("min_stars", 50),
        max_inactive_days=scoring.get("max_inactive_days", 180),
    )
    print(f"📊 {len(scored)} passed algorithmic scoring")

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

    print(f"✅ {len(accepted_tools)} passed AI evaluation")

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
        print(f"🔗 PR created: {pr_url}")

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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_main.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pipeline/main.py tests/test_main.py
git commit -m "feat: main pipeline orchestrator wiring all gates together"
```

---

### Task 13: GitHub Actions workflow

**Files:**
- Create: `.github/workflows/discover.yml`

- [ ] **Step 1: Create workflow file**

```yaml
# .github/workflows/discover.yml
name: Discover CLI Tools

on:
  schedule:
    # Every Monday at 00:00 UTC
    - cron: '0 0 * * 1'
  workflow_dispatch:  # Allow manual trigger

permissions:
  contents: write
  pull-requests: write

jobs:
  discover:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Run discovery pipeline
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          LLM_PROVIDER: ${{ vars.LLM_PROVIDER || 'anthropic' }}
          LLM_MODEL: ${{ vars.LLM_MODEL || 'claude-haiku-4-5-20251001' }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: python -m pipeline.main

      - name: Check for changes
        id: changes
        run: |
          if git diff --quiet; then
            echo "changed=false" >> "$GITHUB_OUTPUT"
          else
            echo "changed=true" >> "$GITHUB_OUTPUT"
          fi
```

- [ ] **Step 2: Commit**

```bash
mkdir -p .github/workflows
git add .github/workflows/discover.yml
git commit -m "feat: GitHub Actions weekly cron workflow for discovery pipeline"
```

---

### Task 14: Seed the repo with initial tools & generate first README

**Files:**
- Modify: `data/tools.yaml`
- Create: `README.md`

- [ ] **Step 1: Seed tools.yaml with well-known CLI tools**

Populate `data/tools.yaml` with ~20 well-known CLI tools across categories as a starting point. These are the "founding" entries that establish the list's quality bar.

Include tools like: ripgrep, fd, bat, eza, fzf, zoxide, starship, jq, yq, httpie, curl, lazygit, delta, dust, bottom, hyperfine, tokei, tldr, atuin, nushell.

- [ ] **Step 2: Run generate.py to build README**

Run: `cd /Users/roy/Documents/Github/awesome-cli-tools && python -c "from pipeline.generate import generate_readme; from pipeline.data import load_tools, load_categories; print(generate_readme(load_tools(), load_categories()))" > README.md`

- [ ] **Step 3: Verify README looks correct**

Run: `head -50 README.md`

- [ ] **Step 4: Commit**

```bash
git add data/tools.yaml README.md
git commit -m "feat: seed with 20 well-known CLI tools and generate initial README"
```

---

### Task 15: Run all tests and verify

- [ ] **Step 1: Install dependencies**

Run: `cd /Users/roy/Documents/Github/awesome-cli-tools && pip install -e ".[dev]"`

- [ ] **Step 2: Run full test suite**

Run: `python -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 3: Run pipeline in dry-run mode**

Run: `python -m pipeline.main --dry-run`
Expected: Pipeline runs without errors (will show 0 candidates without GITHUB_TOKEN, which is fine)

- [ ] **Step 4: Commit any fixes if needed**

---

## Summary

| Task | What | Files |
|------|------|-------|
| 1 | Project scaffolding | pyproject.toml, .gitignore, LICENSE, CONTRIBUTING.md |
| 2 | Data files | data/categories.yaml, sources.yaml, tools.yaml |
| 3 | Data loading | pipeline/data.py, tests/test_data.py |
| 4 | LLM abstraction | pipeline/llm.py, tests/test_llm.py |
| 5 | GitHub Topics source | pipeline/sources/github_topics.py, tests/ |
| 6 | GitHub Trending source | pipeline/sources/github_trending.py, tests/ |
| 7 | Discover orchestrator | pipeline/discover.py, tests/test_discover.py |
| 8 | Algorithmic scoring | pipeline/score.py, tests/test_score.py |
| 9 | AI evaluation | pipeline/evaluate.py, tests/test_evaluate.py |
| 10 | README generation | pipeline/generate.py, templates/, tests/ |
| 11 | PR creation | pipeline/pr.py, tests/test_pr.py |
| 12 | Main pipeline | pipeline/main.py, tests/test_main.py |
| 13 | GitHub Actions | .github/workflows/discover.yml |
| 14 | Seed data + README | data/tools.yaml, README.md |
| 15 | Full verification | Run all tests + dry-run |

**Dependencies:** 1→2→3, 3+4 parallel, 5+6 parallel, 7 needs 5+6, 8 needs 3, 9 needs 4+8, 10 needs 3, 11 needs 9, 12 needs all, 13 needs 12, 14 needs 10+3, 15 needs all.
