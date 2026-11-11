import datetime
import hashlib
import json
import logging
import re
from pathlib import Path
from typing import Optional

from scrivener_assistant.config import ProjectConfig

logger = logging.getLogger(__name__)

VOICE_FILES = {"guide", "hypotheses", "ledger"}
_SLUG_RE = re.compile(r"^[a-z0-9-]+$")
EDIT_CATEGORIES = ("voice", "structure", "tic", "plot", "fidelity")


def edit_id(pair: dict) -> str:
    """Stable id of an edit pair: first 12 hex chars of sha1(op, before, after)."""
    raw = f"{pair.get('op')}\x1f{pair.get('before') or ''}\x1f{pair.get('after') or ''}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]


def normalize_text(text: str) -> str:
    """Lowercase, nbsp -> space, typographic apostrophe -> ', collapsed whitespace."""
    text = (text or "").lower().replace("\u00a0", " ").replace("\u202f", " ").replace("\u2019", "'")
    return re.sub(r"\s+", " ", text).strip()


class VoiceManager:
    """Manages the author-voice files in voice/ (guide, hypotheses, ledger, baseline, exemplars, edits)."""

    def __init__(self, project_path: Path, config: ProjectConfig):
        assistant_folder = Path(config.assistant_folder).expanduser()
        self.base_dir = project_path / assistant_folder / config.voice_subfolder

    # --- guide / hypotheses / ledger ---

    def _validate_name(self, name: str) -> None:
        if name not in VOICE_FILES:
            raise ValueError(f"Unknown voice file '{name}'. Valid names: {sorted(VOICE_FILES)}")

    def get_file(self, name: str) -> Optional[str]:
        self._validate_name(name)
        path = self.base_dir / f"{name}.md"
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def save_file(self, name: str, content: str) -> Path:
        self._validate_name(name)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        path = self.base_dir / f"{name}.md"
        path.write_text(content, encoding="utf-8")
        logger.info(f"Saved voice file '{name}' at {path}")
        return path

    # --- baseline ---

    @property
    def baseline_path(self) -> Path:
        return self.base_dir / "baseline.json"

    def get_baseline(self) -> Optional[dict]:
        if not self.baseline_path.exists():
            return None
        return json.loads(self.baseline_path.read_text(encoding="utf-8"))

    def save_baseline(self, baseline: dict) -> Path:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.baseline_path.write_text(json.dumps(baseline, indent=2, ensure_ascii=False), encoding="utf-8")
        return self.baseline_path

    # --- exemplars ---

    def _exemplar_path(self, slug: str) -> Path:
        if not _SLUG_RE.match(slug or ""):
            raise ValueError(f"Invalid slug '{slug}'. Use lowercase letters, digits and hyphens only ([a-z0-9-]+).")
        return self.base_dir / "exemplars" / f"{slug}.md"

    def save_exemplar(self, slug: str, content: str) -> Path:
        path = self._exemplar_path(slug)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def get_exemplar(self, slug: str) -> Optional[str]:
        path = self._exemplar_path(slug)
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def list_exemplars(self) -> list:
        folder = self.base_dir / "exemplars"
        if not folder.exists():
            return []
        return sorted(p.stem for p in folder.glob("*.md"))

    # --- rewrite diffs ---

    def _edits_path(self, chapter: int) -> Path:
        return self.base_dir / "edits" / f"chapter-{chapter:02d}.json"

    def save_edits(self, chapter: int, data: dict) -> Path:
        path = self._edits_path(chapter)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def get_edits(self, chapter: int) -> Optional[dict]:
        path = self._edits_path(chapter)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    # --- edit labels (kept apart from the edits file: compute_rewrite_diff overwrites it) ---

    def _labels_path(self, chapter: int) -> Path:
        return self.base_dir / "edits" / f"chapter-{chapter:02d}.labels.json"

    def get_edit_labels(self, chapter: int) -> dict:
        path = self._labels_path(chapter)
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def save_edit_labels(self, chapter: int, labels: list) -> dict:
        """Merge labels ({id, category, note?}) into the chapter's label store; returns the full store."""
        store = self.get_edit_labels(chapter)
        now = datetime.datetime.now().isoformat(timespec="seconds")
        for item in labels:
            store[item["id"]] = {
                "category": item["category"],
                "note": item.get("note") or None,
                "labeled_at": now,
            }
        path = self._labels_path(chapter)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(store, indent=2, ensure_ascii=False), encoding="utf-8")
        return store
