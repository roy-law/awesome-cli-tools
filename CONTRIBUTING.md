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
