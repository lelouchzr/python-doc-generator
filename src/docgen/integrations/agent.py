"""Integration with python-agent-runtime."""

from collections.abc import Callable, Sequence

from agent import CallableLLM, ConversationHistory, Runtime, RuntimeConfig, ToolRegistry
from agent.messages import Message
from agent.rag import RAGBackend
from agent.runtime import LLM as RuntimeLLM

from docgen.config import DocgenConfig, LLMProvider
from docgen.integrations.llms import ProviderLLM

SectionRenderer = Callable[[Sequence[Message]], str]


class DocumentationAgent:
    """Runs documentation section generation through the reusable agent runtime."""

    def __init__(self, config: DocgenConfig | None = None) -> None:
        self._config = config or DocgenConfig()
        self._runtime = Runtime()

    def generate(
        self,
        *,
        prompt: str,
        renderer: SectionRenderer,
        rag_backend: RAGBackend | None = None,
        rag_results: int = 5,
    ) -> str:
        llm: RuntimeLLM
        if self._config.llm_provider is LLMProvider.LOCAL:
            llm = CallableLLM(renderer)
            user_input = prompt
        else:
            llm = ProviderLLM(
                self._config.llm_provider,
                model=self._config.llm_model,
                max_tokens=self._config.max_tokens,
            )
            user_input = _hosted_prompt(prompt, renderer)
        return self._runtime.run(
            user_input,
            llm=llm,
            history=ConversationHistory(),
            tools=ToolRegistry(),
            config=RuntimeConfig(
                instructions=(
                    "Generate concise, useful Markdown documentation from repository "
                    "analysis facts. Prefer concrete file paths and practical guidance."
                ),
                enable_rag=rag_backend is not None,
                max_rag_results=rag_results,
                save_history=False,
            ),
            rag=rag_backend,
        )


def _hosted_prompt(prompt: str, renderer: SectionRenderer) -> str:
    draft = renderer(())
    return "\n\n".join(
        [
            prompt,
            "Use the deterministic repository analysis draft below as factual grounding.",
            "Rewrite and improve it as polished Markdown. Do not invent unsupported facts.",
            draft,
        ]
    )
