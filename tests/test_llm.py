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
