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
