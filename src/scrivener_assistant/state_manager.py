from pathlib import Path
from typing import Optional
import logging
from scrivener_assistant.config import ProjectConfig

logger = logging.getLogger(__name__)

STATE_FILES = ["situation", "characters", "knowledge", "inventory"]


class StateManager:
    """Manages versioned per-chapter state in state/current/ and state/chapter-NN/."""

    def __init__(self, project_path: Path, config: ProjectConfig):
        self.base_dir = project_path / config.assistant_folder / config.state_subfolder

    def _chapter_folder(self, chapter: int) -> Path:
        return self.base_dir / f"chapter-{chapter:02d}"

    def _read_state_dir(self, directory: Path) -> Optional[dict]:
        if not directory.exists():
            return None
        result = {}
        for name in STATE_FILES:
            path = directory / f"{name}.md"
            result[name] = path.read_text(encoding="utf-8") if path.exists() else ""
        return result

    def get_current(self) -> Optional[dict]:
        return self._read_state_dir(self.base_dir / "current")

    def get_chapter(self, chapter: int) -> Optional[dict]:
        return self._read_state_dir(self._chapter_folder(chapter))

    def save_state(self, chapter: int, situation: str, characters: str, knowledge: str, inventory: str) -> Path:
        current_dir = self.base_dir / "current"

        # Archive existing current state before overwriting
        if current_dir.exists():
            archive_dir = self._chapter_folder(chapter)
            if not archive_dir.exists():
                archive_dir.mkdir(parents=True, exist_ok=True)
                for name in STATE_FILES:
                    src = current_dir / f"{name}.md"
                    if src.exists():
                        dst = archive_dir / f"{name}.md"
                        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
                logger.info(f"Archived state to {archive_dir}")

        current_dir.mkdir(parents=True, exist_ok=True)
        values = dict(situation=situation, characters=characters, knowledge=knowledge, inventory=inventory)
        for name, content in values.items():
            (current_dir / f"{name}.md").write_text(content, encoding="utf-8")

        logger.info(f"Saved current state (chapter {chapter:02d})")
        return current_dir

    def list_snapshots(self) -> list:
        if not self.base_dir.exists():
            return []
        return sorted(p.name for p in self.base_dir.iterdir() if p.is_dir() and p.name != "current")
