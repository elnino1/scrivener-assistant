"""
Configuration for Scrivener Assistant project.
"""
from dataclasses import dataclass


@dataclass
class ProjectConfig:
    """
    Configuration for Scrivener project assistant features.
    """
    assistant_folder: str = ".ai-assistant"
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
