from __future__ import annotations

from typing import AsyncGenerator


class _StubAIClient:
    """Placeholder AI client — replace with real Anthropic/OpenAI implementation."""

    async def stream_message(self, prompt: str) -> AsyncGenerator[str, None]:
        raise NotImplementedError("AI client not yet implemented")
        # Required to make this a generator
        yield  # type: ignore[misc]

    async def complete_message(self, prompt: str) -> str:
        raise NotImplementedError("AI client not yet implemented")


def get_ai_client() -> _StubAIClient:
    """Return the AI client instance."""
    return _StubAIClient()
