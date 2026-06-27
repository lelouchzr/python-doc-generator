"""Prompt templates used by the agent runtime wrapper."""


def section_prompt(section: str, project_name: str) -> str:
    """Build a compact section generation prompt."""
    return f"Generate the {section} documentation section for {project_name}."

