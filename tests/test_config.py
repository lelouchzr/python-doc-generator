from pathlib import Path

import pytest

from docgen.config import LLMProvider, Section, load_config, merge_config
from docgen.exceptions import LLMProviderError
from docgen.integrations.llms import ProviderLLM


def test_load_config_reads_docgen_table(tmp_path: Path) -> None:
    config_path = tmp_path / "docgen.toml"
    config_path.write_text(
        "\n".join(
            [
                "[docgen]",
                'output_dir = "docs-out"',
                'sections = ["readme", "api"]',
                'exclude = [".venv", "*.sqlite"]',
                'llm = "openai"',
                'model = "gpt-5.5"',
                "max_tokens = 900",
            ]
        ),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.output_dir == Path("docs-out")
    assert config.sections == (Section.README, Section.API)
    assert config.exclude == (".venv", "*.sqlite")
    assert config.llm_provider is LLMProvider.OPENAI
    assert config.llm_model == "gpt-5.5"
    assert config.max_tokens == 900


def test_merge_config_applies_cli_overrides() -> None:
    config = merge_config(load_config(None), llm_provider=LLMProvider.GEMINI)

    assert config.llm_provider is LLMProvider.GEMINI


def test_provider_llm_rejects_local_provider() -> None:
    with pytest.raises(LLMProviderError):
        ProviderLLM(LLMProvider.LOCAL, model=None, max_tokens=1000)
