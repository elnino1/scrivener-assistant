"""Agent instructions shared by Claude Code subagents and MCP prompts."""

import re
from pathlib import Path

_NAME_RE = re.compile(r"^[a-z0-9_]+$")


def load_agent_prompt(name: str) -> str:
    """Return the text of ``<name>.md`` located next to this module."""
    if not isinstance(name, str) or not _NAME_RE.fullmatch(name):
        raise ValueError(f"Invalid agent prompt name: {name!r}")
    path = Path(__file__).parent / f"{name}.md"
    if not path.is_file():
        raise ValueError(f"Unknown agent prompt: {name!r}")
    return path.read_text(encoding="utf-8")
