from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx
from openai import OpenAI

from research_agent.utils import parse_json_object


class LLMConfigurationError(RuntimeError):
    pass


class OllamaConnectionError(RuntimeError):
    pass


@dataclass
class OpenAIChatClient:
    model: str | None = None
    api_key: str | None = None
    base_url: str | None = None
    temperature: float = 0.2

    def __post_init__(self) -> None:
        self.model = self.model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.api_key = self.api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = self.base_url or os.getenv("OPENAI_BASE_URL")

        if not self.api_key:
            raise LLMConfigurationError(
                "OPENAI_API_KEY is missing. Create a .env file or set the variable in your shell."
            )

        kwargs: dict[str, Any] = {"api_key": self.api_key}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        self.client = OpenAI(**kwargs)

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float | None = None,
        json_mode: bool = False,
    ) -> str:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.temperature if temperature is None else temperature,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        return (content or "").strip()

    def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float | None = None,
    ) -> dict[str, Any]:
        text = self.complete(
            system_prompt,
            user_prompt,
            temperature=temperature,
            json_mode=True,
        )
        return parse_json_object(text)


@dataclass
class OllamaChatClient:
    model: str | None = None
    base_url: str | None = None
    temperature: float = 0.2

    def __post_init__(self) -> None:
        self.model = self.model or os.getenv("OLLAMA_MODEL", "llama3.1")
        self.base_url = (self.base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float | None = None,
        json_mode: bool = False,
    ) -> str:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": {
                "temperature": self.temperature if temperature is None else temperature,
            },
        }
        if json_mode:
            payload["format"] = "json"

        try:
            response = httpx.post(f"{self.base_url}/api/chat", json=payload, timeout=120)
            response.raise_for_status()
        except httpx.ConnectError as exc:
            raise OllamaConnectionError(
                "Ollama is not running. Install Ollama, run `ollama pull llama3.1`, "
                "then start Ollama and try again."
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise OllamaConnectionError(
                f"Ollama returned an error: {exc.response.text}"
            ) from exc

        data = response.json()
        return str(data.get("message", {}).get("content", "")).strip()

    def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float | None = None,
    ) -> dict[str, Any]:
        text = self.complete(
            system_prompt,
            user_prompt,
            temperature=temperature,
            json_mode=True,
        )
        return parse_json_object(text)


def create_llm_client() -> OpenAIChatClient | OllamaChatClient:
    provider = os.getenv("LLM_PROVIDER", "").strip().lower()

    if provider in {"openai", "openai-compatible"}:
        return OpenAIChatClient()

    if provider in {"ollama", "local"}:
        return OllamaChatClient()

    if os.getenv("OPENAI_API_KEY"):
        return OpenAIChatClient()

    return OllamaChatClient()
