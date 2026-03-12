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
