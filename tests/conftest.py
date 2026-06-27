from pathlib import Path

import pytest


@pytest.fixture()
def sample_repo(tmp_path: Path) -> Path:
    root = tmp_path / "sample"
    package = root / "sample"
    tests = root / "tests"
    package.mkdir(parents=True)
    tests.mkdir()
    (root / "pyproject.toml").write_text(
        "\n".join(
            [
                "[project]",
                'name = "sample"',
                'version = "0.1.0"',
                'dependencies = ["pydantic>=2"]',
                "",
                "[project.optional-dependencies]",
                'dev = ["pytest>=8"]',
            ]
        ),
        encoding="utf-8",
    )
    (root / "README.md").write_text("# Sample\n\nA sample repository.", encoding="utf-8")
    (package / "__init__.py").write_text(
        '"""Sample package."""\n\nfrom sample.core import Service\n',
        encoding="utf-8",
    )
    (package / "core.py").write_text(
        "\n".join(
            [
                '"""Core services."""',
                "",
                "class Service:",
                '    """Coordinates work."""',
                "",
                "    def run(self, value: str) -> str:",
                '        """Return the processed value."""',
                "        return value.upper()",
            ]
        ),
        encoding="utf-8",
    )
    (tests / "test_core.py").write_text(
        "def test_placeholder():\n    assert True\n",
        encoding="utf-8",
    )
    return root
