from pathlib import Path
from typing import Optional
import logging
from scrivener_assistant.config import ProjectConfig

logger = logging.getLogger(__name__)

DRAFT_FILES = {"brainstorm", "beats", "draft"}


class DraftManager:
    """Manages working files per chapter in drafts/chapter-NN/."""

    def __init__(self, project_path: Path, config: ProjectConfig):
        self.base_dir = project_path / config.assistant_folder / config.drafts_subfolder

    def _chapter_dir(self, chapter: int) -> Path:
        return self.base_dir / f"chapter-{chapter:02d}"

    def save_file(self, chapter: int, file_type: str, content: str) -> Path:
        if file_type not in DRAFT_FILES:
            raise ValueError(f"Unknown file type '{file_type}'. Valid types: {sorted(DRAFT_FILES)}")
        chapter_dir = self._chapter_dir(chapter)
        chapter_dir.mkdir(parents=True, exist_ok=True)
        path = chapter_dir / f"{file_type}.md"
        path.write_text(content, encoding="utf-8")
        logger.info(f"Saved {file_type} for chapter {chapter:02d} at {path}")
        return path

    def get_file(self, chapter: int, file_type: str) -> Optional[str]:
        path = self._chapter_dir(chapter) / f"{file_type}.md"
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def list_chapters(self) -> list:
        if not self.base_dir.exists():
            return []
        return sorted(
            p.name for p in self.base_dir.iterdir()
            if p.is_dir() and any(p.glob("*.md"))
        )
