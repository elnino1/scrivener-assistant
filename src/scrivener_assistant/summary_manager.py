from pathlib import Path
from typing import Optional
import logging
from scrivener_assistant.config import ProjectConfig
from scrivener_assistant.base_manager import BaseSceneDataManager

logger = logging.getLogger(__name__)

class SummaryManager(BaseSceneDataManager):
    """
    Manages loading and saving document summaries in .ai-assistant/summaries/.
    Supports hierarchical storage based on Scrivener binder structure.
    """
    
    def __init__(self, project_path: Path, config: Optional[ProjectConfig] = None, binder_map: Optional[dict] = None):
        cfg = config or ProjectConfig.default()
        super().__init__(project_path, cfg.summaries_subfolder, cfg, binder_map)
        logger.debug(f"SummaryManager initialized for {project_path}")
        
    def save_summary(self, uuid: str, content: str) -> Path:
        """Saves a summary for a specific UUID."""
        return self.save_data(uuid, content)

    def get_summary(self, uuid: str) -> Optional[str]:
        """Retrieves the summary for a specific UUID."""
        return self.get_data(uuid)
