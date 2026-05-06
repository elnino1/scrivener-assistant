import json
import shutil
from pathlib import Path

import pytest

from scrivener_assistant.config import ProjectConfig
from scrivener_assistant.scene_registry_manager import SceneRegistryManager

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_SCRIV = FIXTURES_DIR / "sample.scriv"

# UUID of the single "Scene" Text node under the DraftFolder/Chapter in the fixture
SCENE_UUID = "0A7EDD9F-9DE0-4CC9-9AC1-EE0E3769B6A8"


@pytest.fixture
def temp_project(tmp_path):
    dest = tmp_path / "temp.scriv"
    shutil.copytree(SAMPLE_SCRIV, dest)
    return dest


@pytest.fixture
def project_with_registry(temp_project):
    """Returns a ScrivenerProject loaded from the temp copy."""
    from scrivener_assistant.project import ScrivenerProject
    return ScrivenerProject(str(temp_project))


# --- registry path ---

def test_registry_path_inside_ai_assistant(temp_project):
    config = ProjectConfig()
    mgr = SceneRegistryManager(temp_project, config)
    assert mgr.registry_path.parent == temp_project / ".ai-assistant"
    assert mgr.registry_path.name == "scene_registry.json"


def test_registry_path_respects_custom_folder(temp_project):
    config = ProjectConfig(assistant_folder=".custom-ai")
    mgr = SceneRegistryManager(temp_project, config)
    assert mgr.registry_path.parent == temp_project / ".custom-ai"


# --- get_registry when no file ---

def test_get_registry_returns_none_when_absent(temp_project):
    config = ProjectConfig()
    mgr = SceneRegistryManager(temp_project, config)
    assert mgr.get_registry() is None


# --- rebuild ---

def test_rebuild_creates_json_file(project_with_registry):
    project_with_registry.scene_registry.rebuild(project_with_registry)
    assert project_with_registry.scene_registry.registry_path.exists()


def test_rebuild_produces_valid_json(project_with_registry):
    project_with_registry.scene_registry.rebuild(project_with_registry)
    data = project_with_registry.scene_registry.get_registry()
    assert data is not None
    assert "scenes" in data
    assert "scene_count" in data
    assert isinstance(data["scenes"], list)


def test_rebuild_only_includes_text_nodes(project_with_registry):
    project_with_registry.scene_registry.rebuild(project_with_registry)
    data = project_with_registry.scene_registry.get_registry()
    for scene in data["scenes"]:
        assert scene["type"] == "Text"


def test_rebuild_scene_count_matches_scenes(project_with_registry):
    project_with_registry.scene_registry.rebuild(project_with_registry)
    data = project_with_registry.scene_registry.get_registry()
    assert data["scene_count"] == len(data["scenes"])


def test_rebuild_scene_has_required_fields(project_with_registry):
    project_with_registry.scene_registry.rebuild(project_with_registry)
    data = project_with_registry.scene_registry.get_registry()
    required = {"uuid", "title", "type", "binder_path", "word_count",
                "synopsis", "custom_metadata", "summary", "has_review", "review_updated_at"}
    for scene in data["scenes"]:
        assert required.issubset(scene.keys()), f"Missing keys in scene {scene['uuid']}"


def test_rebuild_binder_path_is_list_of_strings(project_with_registry):
    project_with_registry.scene_registry.rebuild(project_with_registry)
    data = project_with_registry.scene_registry.get_registry()
    for scene in data["scenes"]:
        assert isinstance(scene["binder_path"], list)
        assert all(isinstance(s, str) for s in scene["binder_path"])


def test_rebuild_word_count_is_int(project_with_registry):
    project_with_registry.scene_registry.rebuild(project_with_registry)
    data = project_with_registry.scene_registry.get_registry()
    for scene in data["scenes"]:
        assert isinstance(scene["word_count"], int)
        assert scene["word_count"] >= 0


def test_rebuild_synopsis_from_fixture(project_with_registry):
    # Fixture has synopsis.txt for 684ADA52-4D45-48D2-B03D-5ECB784963EE (Title Page)
    project_with_registry.scene_registry.rebuild(project_with_registry)
    data = project_with_registry.scene_registry.get_registry()
    scenes_by_uuid = {s["uuid"]: s for s in data["scenes"]}
    title_page = scenes_by_uuid.get("684ADA52-4D45-48D2-B03D-5ECB784963EE")
    assert title_page is not None
    assert title_page["synopsis"] is not None
    assert len(title_page["synopsis"]) > 0


def test_rebuild_no_summary_returns_null(project_with_registry):
    project_with_registry.scene_registry.rebuild(project_with_registry)
    data = project_with_registry.scene_registry.get_registry()
    for scene in data["scenes"]:
        assert scene["summary"] is None or isinstance(scene["summary"], str)


def test_rebuild_has_review_false_when_no_review(project_with_registry):
    project_with_registry.scene_registry.rebuild(project_with_registry)
    data = project_with_registry.scene_registry.get_registry()
    for scene in data["scenes"]:
        assert scene["has_review"] is False
        assert scene["review_updated_at"] is None


def test_rebuild_summary_included_after_save(project_with_registry):
    project_with_registry.save_summary(SCENE_UUID, "A brave new scene.")
    project_with_registry.scene_registry.rebuild(project_with_registry)
    data = project_with_registry.scene_registry.get_registry()
    scenes_by_uuid = {s["uuid"]: s for s in data["scenes"]}
    assert scenes_by_uuid[SCENE_UUID]["summary"] == "A brave new scene."


def test_rebuild_has_review_true_after_save(project_with_registry):
    project_with_registry.save_review(SCENE_UUID, "Good pacing.")
    project_with_registry.scene_registry.rebuild(project_with_registry)
    data = project_with_registry.scene_registry.get_registry()
    scenes_by_uuid = {s["uuid"]: s for s in data["scenes"]}
    assert scenes_by_uuid[SCENE_UUID]["has_review"] is True
    assert scenes_by_uuid[SCENE_UUID]["review_updated_at"] is not None


# --- get_scene ---

def test_get_scene_returns_single_entry(project_with_registry):
    project_with_registry.scene_registry.rebuild(project_with_registry)
    scene = project_with_registry.scene_registry.get_scene(SCENE_UUID)
    assert scene is not None
    assert scene["uuid"] == SCENE_UUID


def test_get_scene_returns_none_for_unknown_uuid(project_with_registry):
    project_with_registry.scene_registry.rebuild(project_with_registry)
    assert project_with_registry.scene_registry.get_scene("DOES-NOT-EXIST") is None


def test_get_scene_returns_none_when_registry_absent(temp_project):
    config = ProjectConfig()
    mgr = SceneRegistryManager(temp_project, config)
    assert mgr.get_scene(SCENE_UUID) is None
