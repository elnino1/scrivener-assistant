from pathlib import Path
from typing import Optional, List
import logging
import os
import shutil
from scrivener_assistant.config import ProjectConfig
from scrivener_assistant.path_utils import generate_hybrid_filename, slugify, get_short_uuid
from scrivener_assistant.binder_parser import BinderNode

logger = logging.getLogger(__name__)

class BaseSceneDataManager:
    """
    Base class for managing scene-related data (summaries, reviews, etc.)
    under .ai-assistant/ in a hierarchical structure.
    """
    def __init__(self, project_path: Path, subfolder: str, config: Optional[ProjectConfig] = None, binder_map: Optional[dict[str, BinderNode]] = None):
        self.project_path = project_path
        self.config = config or ProjectConfig.default()
        self.base_dir = self.project_path / self.config.assistant_folder / subfolder
        self._binder_map = binder_map
        
    def set_binder_map(self, binder_map: dict[str, BinderNode]):
        """Sets the binder map for path resolution."""
        self._binder_map = binder_map

    def _get_hierarchical_path(self, uuid: str) -> Path:
        """
        Resolves the hierarchical path for a given UUID.
        Example: summaries/Draft/Chapter 1/Scene Name--UUID.md
        """
        if not self._binder_map or uuid not in self._binder_map:
            # Fallback to flat UUID naming if binder structure unknown
            return self.base_dir / f"{uuid}.md"
            
        node = self._binder_map[uuid]
        path_titles = node.get_path()
        
        # Build relative folder path from slugified titles (excluding the node itself)
        # Note: We keep the direct hierarchy. 
        # path_titles[-1] is the scene title itself.
        folder_slugs = [slugify(title) for title in path_titles[:-1]]
        filename = generate_hybrid_filename(node.title, uuid)
        
        return self.base_dir.joinpath(*folder_slugs) / filename

    def _find_existing_file(self, uuid: str) -> Optional[Path]:
        """
        Attempts to find an existing file for this UUID anywhere in the base_dir.
        Matches by --{short_uuid}.md suffix or {uuid}.md.
        """
        if not self.base_dir.exists():
            return None
            
        short_uuid = get_short_uuid(uuid)
        
        # Search for either exact UUID or hybrid name pattern
        for p in self.base_dir.rglob("*.md"):
            # Matches:
            # - {UUID}.md
            # - anytitle--{short_uuid}.md
            # - {short_uuid}.md
            if p.stem == uuid or p.stem.endswith(f"--{short_uuid}") or p.stem == short_uuid:
                return p
        return None

    def save_data(self, uuid: str, content: str) -> Path:
        """Saves data to a hierarchical path, moving existing files if needed."""
        target_path = self._get_hierarchical_path(uuid)
        existing_path = self._find_existing_file(uuid)
        
        if existing_path and existing_path != target_path:
            logger.info(f"Moving existing data from {existing_path} to {target_path}")
            # Ensure target directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            # If target exists (unexpected), remove it first or existing_path.rename will fail
            if target_path.exists():
                target_path.unlink()
            existing_path.rename(target_path)
        else:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
        target_path.write_text(content, encoding="utf-8")
        logger.info(f"Saved data for {uuid} at {target_path}")
        
        # Clean up empty parent directories if we moved something
        if existing_path and existing_path.parent != target_path.parent:
            self._cleanup_empty_dirs(existing_path.parent)
            
        return target_path

    def get_data(self, uuid: str) -> Optional[str]:
        """Retrieves data for a given UUID."""
        # Try expected path first
        target_path = self._get_hierarchical_path(uuid)
        if target_path.exists():
            return target_path.read_text(encoding="utf-8")
            
        # Fallback to search
        existing_path = self._find_existing_file(uuid)
        if existing_path:
            # Found it elsewhere, might want to move it now?
            # For now just return content
            return existing_path.read_text(encoding="utf-8")
            
        return None

    def list_items(self) -> List[str]:
        """
        Lists available items in the base directory.
        Returns a list of names (stems) of the .md files.
        """
        if not self.base_dir.exists():
            return []
            
        items = []
        # Walk through all files
        for p in self.base_dir.rglob("*.md"):
            # We return the stem, which is the filename without extension.
            # If it follows the hybrid pattern (Name--UUID), we might want to return just the Name?
            # For now, let's return the stem as is, or maybe clean it up if it looks like a hybrid.
            stem = p.stem
            if "--" in stem:
                # Heuristic: if it has --UUID at the end, show the name part
                parts = stem.split("--")
                # Assuming the last part is UUID-ish, join the rest
                items.append("--".join(parts[:-1]))
            else:
                items.append(stem)
                
        return sorted(items)

    def _cleanup_empty_dirs(self, directory: Path):
        """Recursively removes empty directories up to base_dir."""
        try:
            while directory != self.base_dir and directory.is_dir() and not any(directory.iterdir()):
                logger.debug(f"Cleaning up empty directory: {directory}")
                directory.rmdir()
                directory = directory.parent
        except Exception as e:
            logger.warning(f"Failed to cleanup directory {directory}: {e}")
