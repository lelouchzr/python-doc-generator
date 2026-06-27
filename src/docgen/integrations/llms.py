"""Optional LLM provider adapters for the agent runtime."""

from collections.abc import Sequence
from importlib import import_module
from typing import Any

from agent.messages import Message

from docgen.config import LLMProvider
from docgen.exceptions import LLMProviderError

DEFAULT_MODELS: dict[LLMProvider, str] = {
    LLMProvider.OPENAI: "gpt-5.5",
    LLMProvider.ANTHROPIC: "claude-opus-4-8",
    LLMProvider.GEMINI: "gemini-3.5-flash",
}


class ProviderLLM:
    """Agent-runtime compatible adapter for hosted LLM providers."""

    def __init__(self, provider: LLMProvider, *, model: str | None, max_tokens: int) -> None:
        if provider is LLMProvider.LOCAL:
            msg = "ProviderLLM is only for hosted providers."
            raise LLMProviderError(msg)
        self._provider = provider
        self._model = model or DEFAULT_MODELS[provider]
        self._max_tokens = max_tokens

    @property
    def model(self) -> str:
        return self._model

    def complete(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[dict[str, Any]] | None = None,
    ) -> str:
        del tools
        if self._provider is LLMProvider.OPENAI:
            return self._complete_openai(messages)
        if self._provider is LLMProvider.ANTHROPIC:
            return self._complete_anthropic(messages)
        if self._provider is LLMProvider.GEMINI:
            return self._complete_gemini(messages)
        msg = f"Unsupported LLM provider: {self._provider}"
        raise LLMProviderError(msg)

    def _complete_openai(self, messages: Sequence[Message]) -> str:
        module = _import_optional("openai", "Install with `uv sync --extra openai`.")
        client = module.OpenAI()
        response = client.responses.create(
            model=self._model,
            input=[
                {
                    "role": "developer" if message.role == "system" else message.role,
                    "content": message.content,
                }
                for message in messages
                if message.role != "tool"
            ],
        )
        return _as_text(getattr(response, "output_text", None))

    def _complete_anthropic(self, messages: Sequence[Message]) -> str:
        module = _import_optional("anthropic", "Install with `uv sync --extra anthropic`.")
        client = module.Anthropic()
        system = "\n\n".join(message.content for message in messages if message.role == "system")
        api_messages = [
            {
                "role": "assistant" if message.role == "assistant" else "user",
                "content": message.content,
            }
            for message in messages
            if message.role in {"user", "assistant"}
        ]
        response = client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system=system or None,
            messages=api_messages,
        )
        return _anthropic_text(response)

    def _complete_gemini(self, messages: Sequence[Message]) -> str:
        module = _import_optional("google.genai", "Install with `uv sync --extra gemini`.")
        client = module.Client()
        response = client.models.generate_content(
            model=self._model,
            contents=_plain_text_prompt(messages),
        )
        return _as_text(getattr(response, "text", None))


def _import_optional(module_name: str, install_hint: str) -> Any:
    try:
        return import_module(module_name)
    except ImportError as exc:
        msg = f"Missing optional provider dependency `{module_name}`. {install_hint}"
        raise LLMProviderError(msg) from exc


def _plain_text_prompt(messages: Sequence[Message]) -> str:
    return "\n\n".join(f"{message.role.upper()}:\n{message.content}" for message in messages)


def _anthropic_text(response: Any) -> str:
    blocks = getattr(response, "content", ())
    parts: list[str] = []
    for block in blocks:
        if getattr(block, "type", None) == "text":
            parts.append(_as_text(getattr(block, "text", None)))
    return "\n".join(part for part in parts if part).strip()


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)
