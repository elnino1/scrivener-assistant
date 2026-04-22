"""
Configuration for Scrivener Assistant project.
"""
import os
from dataclasses import dataclass, field


@dataclass
class ProjectConfig:
    """
    Configuration for Scrivener project assistant features.
    """
    assistant_folder: str = field(default_factory=lambda: os.getenv("SCRIVENER_ASSISTANT_FOLDER", ".ai-assistant"))
    prompts_subfolder: str = "prompts"
    summaries_subfolder: str = "summaries"
    reviews_subfolder: str = "reviews"
    characters_subfolder: str = "world/characters"
    locations_subfolder: str = "world/locations"
    world_subfolder: str = "world"
    state_subfolder: str = "state"
    drafts_subfolder: str = "drafts"
    max_backups: int = 5
    
    @classmethod
    def default(cls) -> 'ProjectConfig':
        """Returns default configuration."""
        return cls()
