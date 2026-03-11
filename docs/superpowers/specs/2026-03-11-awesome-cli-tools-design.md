# Design: awesome-cli-tools

## Overview

A public GitHub repo that automatically discovers, evaluates, and curates CLI tools using AI. A weekly GitHub Actions cron job finds trending tools, scores them algorithmically, passes survivors through an LLM editorial gate, and opens a PR with proposed additions. The repo self-improves over time.

## Reference Architecture

Borrows from:
- **sindresorhus/awesome** (~330k stars) — formatting standards, quality bar philosophy
- **awesome-selfhosted** (~278k stars) — structured entry metadata (license, language, description)
- **best-of-generator** — algorithmic scoring, automated PR creation, trending detection

## Repo Structure

```
awesome-cli-tools/
├── README.md                  # Auto-generated — DO NOT EDIT
├── data/
│   ├── tools.yaml             # Source of truth — all curated tools
│   ├── sources.yaml           # Discovery source configuration
│   └── categories.yaml        # Category definitions
├── pipeline/
│   ├── discover.py            # Gate 0: Fetch candidates from sources
│   ├── score.py               # Gate 1: Algorithmic filtering
│   ├── evaluate.py            # Gate 2: LLM editorial judgment
│   ├── generate.py            # Render YAML → README.md
│   ├── pr.py                  # Gate 3: Create PR with proposals
│   ├── llm.py                 # LLM abstraction (Claude/OpenAI/etc)
│   └── sources/
│       ├── github_trending.py
│       ├── github_topics.py
│       ├── hackernews.py
│       ├── reddit.py
│       └── awesome_lists.py
├── templates/
│   └── readme.md.jinja        # Jinja2 template for README generation
├── tests/
├── .github/
│   └── workflows/
│       └── discover.yml       # Weekly cron workflow
├── pyproject.toml
├── CONTRIBUTING.md
└── LICENSE (MIT)
```

## Data Model (tools.yaml)

```yaml
- name: ripgrep
  repo: BurntSushi/ripgrep
  url: https://github.com/BurntSushi/ripgrep
  description: "Fast recursive grep alternative written in Rust"
  category: search
  language: Rust
  license: MIT
  stars: 48000
  added_date: 2026-03-11
  discovered_by: github_trending
  ai_summary: "Significantly faster than grep for large codebases..."
```

## Pipeline Flow (Weekly Cron)

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────┐
│  discover.py │───▶│   score.py   │───▶│ evaluate.py │───▶│  pr.py   │
│              │    │              │    │             │    │          │
│ GitHub API   │    │ Stars > 50   │    │ LLM rates   │    │ Creates  │
│ HN, Reddit   │    │ Active 6mo   │    │ novelty &   │    │ GitHub   │
│ Awesome lists│    │ Not archived │    │ quality     │    │ PR with  │
│              │    │ Growth rate  │    │ Writes desc │    │ diff     │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────┘
                                                               │
                                              generate.py ◄────┘
                                              (rebuilds README)
```

## Gate Details

### Gate 0 — Discovery (discover.py)
- GitHub: trending repos, topic search (`cli`, `terminal`, `command-line`, `tui`)
- HN/Reddit: scrape for GitHub links mentioned in relevant subs
- Awesome lists: diff against known lists for new additions
- Deduplicates against existing `tools.yaml`

### Gate 1 — Algorithmic Scoring (score.py)
- Reject: <50 stars, archived, fork, no commits in 6 months
- Score: stars, star growth rate (last 30 days), forks, open issues ratio, contributor count
- Flag "trending": 500+ stars gained in past month

### Gate 2 — AI Editorial (evaluate.py)
- Fetches repo README via GitHub API
- LLM prompt: "Is this a genuine CLI/TUI tool? Is it novel vs what's already listed? Rate quality 1-10. Write a one-line description."
- Reject if quality < 6 or duplicate functionality
- Auto-categorize into existing categories

### Gate 3 — PR Creation (pr.py)
- Adds passing tools to a branch copy of `tools.yaml`
- Runs `generate.py` to rebuild README
- Opens PR with: list of proposed tools, scores, AI reasoning, trending badge if applicable

## Self-Improvement Mechanisms

1. **Source expansion** — new source modules are plug-and-play (add a file to `sources/`)
2. **Threshold tuning** — star minimums, quality scores stored in `sources.yaml`, adjustable over time
3. **Category growth** — AI can propose new categories when tools don't fit existing ones
4. **Stale tool detection** — weekly run also checks existing entries for archived/abandoned repos, opens removal PRs
5. **Auto-merge option** — configurable flag to auto-merge PRs above a confidence threshold (disabled by default)

## Generated README Format

Following awesome-selfhosted's structured style:

```markdown
# Awesome CLI Tools

> An AI-curated list of awesome command-line tools, automatically updated weekly.

## Contents
- [Search](#search)
- [File Management](#file-management)
- ...

## Search

- [ripgrep](https://github.com/BurntSushi/ripgrep) - Fast recursive grep alternative. `Rust` `MIT` ⭐ 48k 🔥
- [fd](https://github.com/sharkdp/fd) - Simple, fast find alternative. `Rust` `MIT` ⭐ 34k
```

🔥 = trending (gained 500+ stars in last month)

## Tech Stack

- Python 3.12+
- `PyGithub` / `httpx` for API calls
- `pyyaml` for data
- `jinja2` for README templating
- LLM via configurable provider (`anthropic` / `openai` SDK)
- GitHub Actions for cron
- `pytest` for tests

## Cron Schedule

- Weekly (every Monday at 00:00 UTC)
- GitHub Actions workflow

## LLM Provider

- Configurable via environment variable (`LLM_PROVIDER=anthropic|openai`)
- Model configurable via `LLM_MODEL` env var
- Tiered approach recommended: cheaper model for bulk screening, capable model for final editorial
