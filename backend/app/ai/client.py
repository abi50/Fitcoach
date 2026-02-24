from __future__ import annotations

from typing import AsyncGenerator

from openai import AsyncOpenAI

from app.config import get_settings


class OpenAIClient:
    """Async OpenAI GPT-4o client with streaming and structured-output support."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = settings.OPENAI_MODEL

    async def stream_json(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4000,
    ) -> AsyncGenerator[str, None]:
        """Stream a JSON response from GPT-4o, yielding raw text chunks.

        The caller accumulates chunks into a complete JSON string.
        Uses response_format=json_object so the model always outputs valid JSON.
        """
        async with self._client.chat.completions.stream(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=max_tokens,
        ) as stream:
            async for text in stream.text_stream:
                if text:
                    yield text

    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 2000,
    ) -> str:
        """Complete a JSON response (non-streaming). Returns raw JSON string."""
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or "{}"


def get_ai_client() -> OpenAIClient:
    """Return the singleton AI client instance."""
    return OpenAIClient()
