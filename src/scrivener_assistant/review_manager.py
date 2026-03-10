from pathlib import Path
from typing import Optional, List, Dict
import json
import datetime
import logging
from scrivener_assistant.config import ProjectConfig
from scrivener_assistant.base_manager import BaseSceneDataManager

logger = logging.getLogger(__name__)

class ReviewManager(BaseSceneDataManager):
    """
    Manages loading and saving style review files in .ai-assistant/reviews/.
    Supports hierarchical storage based on Scrivener binder structure.
    """
    
    def __init__(self, project_path: Path, config: Optional[ProjectConfig] = None, binder_map: Optional[dict] = None):
        cfg = config or ProjectConfig.default()
        super().__init__(project_path, cfg.reviews_subfolder, cfg, binder_map)
        logger.debug(f"ReviewManager initialized for {project_path}")
        
    def save_review(self, uuid: str, content: str) -> Path:
        """Saves a style review for a specific UUID, archiving the previous one if it exists."""
        # Check for existing review and archive it
        existing_path = self._find_existing_file(uuid)
        if existing_path and existing_path.exists():
            self._archive_existing_review(uuid, existing_path)
            
        return self.save_data(uuid, content)

    def get_review(self, uuid: str) -> Optional[str]:
        """Retrieves the style review for a specific UUID."""
        return self.get_data(uuid)

    def _archive_existing_review(self, uuid: str, source_path: Path):
        """Archives the current review file to _archive/{uuid}/{timestamp}.md"""
        try:
            timestamp = datetime.datetime.now().isoformat().replace(":", "-").split(".")[0]
            archive_dir = self.base_dir / "_archive" / uuid
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            archive_path = archive_dir / f"{timestamp}.md"
            import shutil
            shutil.copy2(source_path, archive_path)
            logger.info(f"Archived review for {uuid} to {archive_path}")
        except Exception as e:
            logger.error(f"Failed to archive review for {uuid}: {e}")

    def get_review_history(self, uuid: str) -> List[Dict[str, str]]:
        """
        Returns a list of archived reviews for a given UUID.
        Returns: [{"timestamp": "...", "path": "..."}]
        """
        archive_dir = self.base_dir / "_archive" / uuid
        if not archive_dir.exists():
            return []
            
        history = []
        for p in sorted(archive_dir.glob("*.md"), reverse=True):
            history.append({
                "timestamp": p.stem,
                "path": str(p)
            })
        return history

    def get_archived_review(self, uuid: str, timestamp: str) -> Optional[str]:
        """Retrieves the content of a specific archived review."""
        archive_path = self.base_dir / "_archive" / uuid / f"{timestamp}.md"
        if archive_path.exists():
            return archive_path.read_text(encoding="utf-8")
        return None
