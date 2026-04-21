from pathlib import Path
from typing import Optional
import logging
from scrivener_assistant.config import ProjectConfig

logger = logging.getLogger(__name__)

VALID_SECTIONS = {"style", "bible", "structure", "plan", "timeline", "synthèse", "relations"}


class WorldManager:
    """Manages flat markdown files in world/ (style, bible, structure, plan, timeline, synthèse)."""

    def __init__(self, project_path: Path, config: ProjectConfig):
        self.base_dir = project_path / config.assistant_folder / config.world_subfolder

    def get_section(self, section: str) -> Optional[str]:
        path = self.base_dir / f"{section}.md"
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def get_all(self) -> dict:
        result = {}
        if not self.base_dir.exists():
            return result
        for path in sorted(self.base_dir.glob("*.md")):
            result[path.stem] = path.read_text(encoding="utf-8")
        return result

    def save_section(self, section: str, content: str) -> Path:
        if section not in VALID_SECTIONS:
            raise ValueError(f"Unknown section '{section}'. Valid sections: {sorted(VALID_SECTIONS)}")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        path = self.base_dir / f"{section}.md"
        path.write_text(content, encoding="utf-8")
        logger.info(f"Saved world section '{section}' at {path}")
        return path

    def list_sections(self) -> list:
        if not self.base_dir.exists():
            return []
        return sorted(p.stem for p in self.base_dir.glob("*.md"))
