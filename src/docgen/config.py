"""Configuration for documentation generation."""

import tomllib
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from docgen.exceptions import ConfigError


class Section(StrEnum):
    """Documentation sections supported by the CLI."""

    README = "readme"
    ARCHITECTURE = "architecture"
    API = "api"
    DIAGRAMS = "diagrams"
    QUESTIONS = "questions"
    ROADMAP = "roadmap"
    SUMMARY = "summary"


class LLMProvider(StrEnum):
    """LLM providers supported by documentation generation."""

    LOCAL = "local"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"


DEFAULT_SECTIONS: tuple[Section, ...] = (
    Section.README,
    Section.ARCHITECTURE,
    Section.API,
    Section.DIAGRAMS,
    Section.QUESTIONS,
    Section.ROADMAP,
    Section.SUMMARY,
)


class DocgenConfig(BaseModel):
    """Runtime configuration for repository documentation generation."""

    model_config = ConfigDict(frozen=True)

    output_dir: Path = Path("generated-docs")
    sections: tuple[Section, ...] = DEFAULT_SECTIONS
    max_file_size: int = Field(default=250_000, ge=1_000)
    include_private: bool = False
    rag_results: int = Field(default=5, ge=1, le=20)
    exclude: tuple[str, ...] = ()
    llm_provider: LLMProvider = LLMProvider.LOCAL
    llm_model: str | None = None
    max_tokens: int = Field(default=1_500, ge=100, le=16_000)


def load_config(path: Path | None) -> DocgenConfig:
    """Load a docgen config file, returning defaults when no file exists."""
    if path is None:
        path = Path("docgen.toml")
        if not path.exists():
            return DocgenConfig()

    if not path.exists():
        msg = f"Config file does not exist: {path}"
        raise ConfigError(msg)

    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    data = raw.get("docgen", raw)
    if not isinstance(data, dict):
        msg = "Config file must contain a TOML table."
        raise ConfigError(msg)
    return DocgenConfig(**_normalize_config_data(data))


def merge_config(base: DocgenConfig, **overrides: Any) -> DocgenConfig:
    """Merge CLI overrides into a loaded configuration."""
    clean = {key: value for key, value in overrides.items() if value is not None}
    if not clean:
        return base
    return base.model_copy(update=clean)


def parse_sections(raw: str | list[str] | tuple[str, ...]) -> tuple[Section, ...]:
    """Parse section names from comma-separated CLI text or TOML arrays."""
    values: list[str]
    if isinstance(raw, str):
        values = [item.strip() for item in raw.split(",")]
    else:
        values = [str(item).strip() for item in raw]

    sections: list[Section] = []
    for value in values:
        if not value:
            continue
        try:
            sections.append(Section(value.lower()))
        except ValueError as exc:
            allowed = ", ".join(section.value for section in Section)
            msg = f"Unknown section '{value}'. Allowed sections: {allowed}"
            raise ConfigError(msg) from exc
    return tuple(sections) or DEFAULT_SECTIONS


def parse_exclude(raw: str | list[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    """Parse exclude patterns from comma-separated CLI text or TOML arrays."""
    if raw is None:
        return ()
    if isinstance(raw, str):
        values = [item.strip() for item in raw.split(",")]
    else:
        values = [str(item).strip() for item in raw]
    return tuple(value for value in values if value)


def _normalize_config_data(data: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(data)
    if "sections" in normalized:
        normalized["sections"] = parse_sections(normalized["sections"])
    if "exclude" in normalized:
        normalized["exclude"] = parse_exclude(normalized["exclude"])
    if "output_dir" in normalized:
        normalized["output_dir"] = Path(str(normalized["output_dir"]))
    if "llm" in normalized:
        normalized["llm_provider"] = normalized.pop("llm")
    if "model" in normalized:
        normalized["llm_model"] = normalized.pop("model")
    return normalized
