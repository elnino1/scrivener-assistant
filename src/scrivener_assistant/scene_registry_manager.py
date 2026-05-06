import json
import os
import datetime
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from scrivener_assistant.config import ProjectConfig

if TYPE_CHECKING:
    from scrivener_assistant.project import ScrivenerProject

logger = logging.getLogger(__name__)


class SceneRegistryManager:
    """
    Maintains a single scene_registry.json inside .ai-assistant/ that aggregates
    per-scene metadata for all Text-type binder nodes.
    """

    def __init__(self, project_path: Path, config: ProjectConfig):
        self.project_path = project_path
        self.config = config
        assistant_folder = Path(config.assistant_folder).expanduser()
        self.registry_path = project_path / assistant_folder / config.scene_registry_filename

    def rebuild(self, project: "ScrivenerProject") -> Path:
        """Collect all Text-node data and write the registry atomically."""
        scenes = []
        for uuid, node in project.binder_map.items():
            if node.type != "Text":
                continue
            scenes.append(self._collect_scene(project, uuid, node))

        project_name = project.path.name.removesuffix(".scriv")
        registry = {
            "project": project_name,
            "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
            "scene_count": len(scenes),
            "scenes": scenes,
        }

        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.registry_path.with_suffix(".json.tmp")
        tmp_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp_path, self.registry_path)

        logger.info(f"Scene registry rebuilt: {len(scenes)} scenes → {self.registry_path}")
        return self.registry_path

    def get_registry(self) -> Optional[dict]:
        """Read and parse the current registry JSON; None if file absent."""
        if not self.registry_path.exists():
            return None
        try:
            return json.loads(self.registry_path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error(f"Failed to read scene registry: {e}")
            return None

    def get_scene(self, uuid: str) -> Optional[dict]:
        """Return a single scene entry; None if not found or registry absent."""
        registry = self.get_registry()
        if registry is None:
            return None
        for scene in registry.get("scenes", []):
            if scene.get("uuid") == uuid:
                return scene
        return None

    def _collect_scene(self, project: "ScrivenerProject", uuid: str, node) -> dict:
        """Collect all data for a single scene node."""
        binder_path = node.get_path()

        try:
            content = project.read_document(uuid)
            word_count = len(content.split()) if content else 0
        except Exception:
            word_count = 0

        try:
            synopsis = project.read_synopsis(uuid) or None
        except Exception:
            synopsis = None

        try:
            custom_metadata = project.metadata_manager.get_custom_metadata(uuid)
        except Exception:
            custom_metadata = {}

        try:
            summary = project.summary_manager.get_summary(uuid)
        except Exception:
            summary = None

        has_review = False
        review_updated_at = None
        try:
            review_path = project.review_manager._find_existing_file(uuid)
            if review_path and review_path.exists():
                has_review = True
                mtime = review_path.stat().st_mtime
                review_updated_at = datetime.datetime.fromtimestamp(mtime).isoformat(timespec="seconds")
        except Exception:
            pass

        return {
            "uuid": uuid,
            "title": node.title,
            "type": node.type,
            "binder_path": binder_path,
            "word_count": word_count,
            "synopsis": synopsis,
            "custom_metadata": custom_metadata,
            "summary": summary,
            "has_review": has_review,
            "review_updated_at": review_updated_at,
        }
