import json
import shutil
from pathlib import Path

import pytest

import server
from server import (
    rebuild_scene_registry,
    get_scene_registry,
    set_project_path,
    update_metadata,
    save_summary,
    save_review,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_SCRIV = FIXTURES_DIR / "sample.scriv"
SCENE_UUID = "0A7EDD9F-9DE0-4CC9-9AC1-EE0E3769B6A8"


@pytest.fixture
def temp_project_server(tmp_path):
    dest = tmp_path / "temp_server.scriv"
    shutil.copytree(SAMPLE_SCRIV, dest)
    set_project_path(str(dest))
    return dest


# --- rebuild_scene_registry tool ---

def test_rebuild_scene_registry_no_project():
    server.current_project = None
    result = rebuild_scene_registry()
    assert "No project loaded" in result


def test_rebuild_scene_registry_returns_scene_count(temp_project_server):
    result = rebuild_scene_registry()
    assert "scenes" in result.lower() or "scene" in result.lower()
    # Should mention a number
    assert any(c.isdigit() for c in result)


def test_rebuild_scene_registry_creates_file(temp_project_server):
    rebuild_scene_registry()
    registry_path = temp_project_server / ".ai-assistant" / "scene_registry.json"
    assert registry_path.exists()
    data = json.loads(registry_path.read_text())
    assert "scenes" in data


# --- get_scene_registry tool ---

def test_get_scene_registry_no_project():
    server.current_project = None
    result = get_scene_registry()
    assert "No project loaded" in result


def test_get_scene_registry_not_built_yet(temp_project_server):
    result = get_scene_registry()
    assert "not found" in result.lower() or "no registry" in result.lower() or "absent" in result.lower()


def test_get_scene_registry_full_after_rebuild(temp_project_server):
    rebuild_scene_registry()
    result = get_scene_registry()
    data = json.loads(result)
    assert "scenes" in data
    assert data["scene_count"] == len(data["scenes"])


def test_get_scene_registry_single_scene(temp_project_server):
    rebuild_scene_registry()
    result = get_scene_registry(uuid=SCENE_UUID)
    data = json.loads(result)
    assert data["uuid"] == SCENE_UUID


def test_get_scene_registry_unknown_uuid(temp_project_server):
    rebuild_scene_registry()
    result = get_scene_registry(uuid="DOES-NOT-EXIST")
    assert "not found" in result.lower()


# --- auto-rebuild on update_metadata ---

def test_update_metadata_triggers_registry_rebuild(temp_project_server):
    registry_path = temp_project_server / ".ai-assistant" / "scene_registry.json"
    assert not registry_path.exists()

    update_metadata(SCENE_UUID, "Status", "Done")

    assert registry_path.exists()
    data = json.loads(registry_path.read_text())
    scenes_by_uuid = {s["uuid"]: s for s in data["scenes"]}
    assert scenes_by_uuid[SCENE_UUID]["custom_metadata"].get("Status") == "Done"


# --- auto-rebuild on save_summary ---

def test_save_summary_triggers_registry_rebuild(temp_project_server):
    save_summary(SCENE_UUID, "A tense confrontation.")
    registry_path = temp_project_server / ".ai-assistant" / "scene_registry.json"
    assert registry_path.exists()
    data = json.loads(registry_path.read_text())
    scenes_by_uuid = {s["uuid"]: s for s in data["scenes"]}
    assert scenes_by_uuid[SCENE_UUID]["summary"] == "A tense confrontation."


# --- auto-rebuild on save_review ---

def test_save_review_triggers_registry_rebuild(temp_project_server):
    save_review(SCENE_UUID, "Strong opening beat.")
    registry_path = temp_project_server / ".ai-assistant" / "scene_registry.json"
    assert registry_path.exists()
    data = json.loads(registry_path.read_text())
    scenes_by_uuid = {s["uuid"]: s for s in data["scenes"]}
    assert scenes_by_uuid[SCENE_UUID]["has_review"] is True
