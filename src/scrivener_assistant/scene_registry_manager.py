import json
import os
import datetime
import logging
import unicodedata
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from scrivener_assistant.config import ProjectConfig
from scrivener_assistant.binder_parser import get_all_text_descendants

if TYPE_CHECKING:
    from scrivener_assistant.project import ScrivenerProject

logger = logging.getLogger(__name__)


def _fold(text: str) -> str:
    """Case- and accent-insensitive form of a title."""
    decomposed = unicodedata.normalize("NFKD", text.strip())
    return "".join(c for c in decomposed if not unicodedata.combining(c)).casefold()


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
        """Collect Text-node data from the DraftFolder and write the registry atomically."""
        if project.draft_root is None:
            logger.warning("No DraftFolder found — falling back to all Text nodes in binder")
            text_nodes = [n for n in project.binder_map.values() if n.type == "Text"]
        else:
            text_nodes = get_all_text_descendants(project.draft_root)

        scenes = []
        for node in text_nodes:
            scenes.append(self._collect_scene(project, node.uuid, node))

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

    def resolve_chapter(self, chapter: str, project: "ScrivenerProject") -> dict:
        """
        Resolve a chapter (1-based number such as "3", or a title) to its scenes.

        A chapter is a top-level child of the DraftFolder (binder_path[1]) that holds at
        least one Text document; chapters are numbered in registry (binder) order.
        If the chapter node is itself a Text document, its only scene is that document.
        Titles match case/accent-insensitively: exact match first, then unique prefix.
        Rebuilds the registry when it is missing.

        Returns {number, title, scenes: [{uuid, title, word_count}]}; raises ValueError
        when the chapter is not found or the title is ambiguous.
        """
        registry = self.get_registry()
        if registry is None:
            self.rebuild(project)
            registry = self.get_registry()
        chapters = []  # consecutive runs of the same binder_path[1]
        for scene in (registry or {}).get("scenes", []):
            path = scene.get("binder_path") or []
            if len(path) < 2:
                continue
            title = path[1]
            if not chapters or chapters[-1]["title"] != title:
                chapters.append({"title": title, "scenes": []})
            chapters[-1]["scenes"].append({
                "uuid": scene["uuid"],
                "title": scene.get("title", ""),
                "word_count": scene.get("word_count", 0),
            })
        if not chapters:
            raise ValueError("No chapters found in the scene registry (is the DraftFolder empty?).")

        query = str(chapter).strip()
        if query.isdigit():
            number = int(query)
            if not 1 <= number <= len(chapters):
                raise ValueError(f"Chapter {number} not found: the project has {len(chapters)} chapters.")
            index = number - 1
        else:
            folded = _fold(query)
            if not folded:
                raise ValueError("Empty chapter reference.")
            exact = [i for i, c in enumerate(chapters) if _fold(c["title"]) == folded]
            matches = exact or [i for i, c in enumerate(chapters) if _fold(c["title"]).startswith(folded)]
            if not matches:
                raise ValueError(f"Chapter '{chapter}' not found.")
            if len(matches) > 1:
                options = ", ".join(f"{i + 1}. {chapters[i]['title']}" for i in matches)
                raise ValueError(f"Chapter '{chapter}' is ambiguous: {options}. Use the chapter number.")
            index = matches[0]
        found = chapters[index]
        return {"number": index + 1, "title": found["title"], "scenes": found["scenes"]}

    def _collect_scene(self, project: "ScrivenerProject", uuid: str, node) -> dict:
        """Collect all data for a single scene node."""
        binder_path = node.get_path()

        try:
            content = project.read_document(uuid)
            word_count = len(content.split()) if content else 0
        except Exception:
            word_count = 0

        try:
            status = project.metadata_manager.get_native_status(uuid)
        except Exception:
            status = None

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
            "status": status,
            "word_count": word_count,
            "synopsis": synopsis,
            "custom_metadata": custom_metadata,
            "summary": summary,
            "has_review": has_review,
            "review_updated_at": review_updated_at,
        }
