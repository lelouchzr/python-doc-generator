"""Project-specific exceptions."""


class DocgenError(RuntimeError):
    """Base exception for documentation generation failures."""


class RepositoryNotFoundError(DocgenError):
    """Raised when the requested repository path does not exist."""


class RepositoryScanError(DocgenError):
    """Raised when the repository cannot be scanned."""


class UnknownSectionError(DocgenError):
    """Raised when the user requests an unsupported documentation section."""


class ConfigError(DocgenError):
    """Raised when a configuration file or CLI override is invalid."""


class LLMProviderError(DocgenError):
    """Raised when an optional LLM provider cannot be configured or called."""
