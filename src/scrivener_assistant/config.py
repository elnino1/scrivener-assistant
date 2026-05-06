"""
Configuration for Scrivener Assistant project.
"""
import os
from dataclasses import dataclass, field


def _resolve_assistant_folder() -> str:
    """
    Read SCRIVENER_ASSISTANT_FOLDER and fall back to the default when the
    variable is absent, empty, or contains an unresolved manifest template
    placeholder (e.g. "${user_config.storage_path}" passed literally by the
    Claude Desktop Extension when the field is left blank).
    """
    value = os.getenv("SCRIVENER_ASSISTANT_FOLDER", "").strip()
    if not value or value.startswith("${"):
        return ".ai-assistant"
    return value


@dataclass
class ProjectConfig:
    """
    Configuration for Scrivener project assistant features.
    """
    assistant_folder: str = field(default_factory=_resolve_assistant_folder)
    prompts_subfolder: str = "prompts"
    summaries_subfolder: str = "summaries"
    reviews_subfolder: str = "reviews"
    characters_subfolder: str = "world/characters"
    locations_subfolder: str = "world/locations"
    world_subfolder: str = "world"
    state_subfolder: str = "state"
    drafts_subfolder: str = "drafts"
    scene_registry_filename: str = "scene_registry.json"
    max_backups: int = 5
    
    @classmethod
    def default(cls) -> 'ProjectConfig':
        """Returns default configuration."""
        return cls()
