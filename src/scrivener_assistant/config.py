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
    characters_subfolder: str = "characters"
    locations_subfolder: str = "locations"
    max_backups: int = 5
    
    @classmethod
    def default(cls) -> 'ProjectConfig':
        """Returns default configuration."""
        return cls()
