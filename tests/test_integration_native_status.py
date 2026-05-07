import json
import shutil
from pathlib import Path

import pytest

import server
from server import (
    list_native_statuses,
    update_native_status,
    rebuild_scene_registry,
    set_project_path,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_SCRIV = FIXTURES_DIR / "sample.scriv"
SCENE_UUID = "0A7EDD9F-9DE0-4CC9-9AC1-EE0E3769B6A8"


@pytest.fixture
def temp_project_server(tmp_path):
    dest = tmp_path / "temp.scriv"
    shutil.copytree(SAMPLE_SCRIV, dest)
    set_project_path(str(dest))
    return dest


def test_list_native_statuses_no_project():
    server.current_project = None
    assert "No project loaded" in list_native_statuses()


def test_update_native_status_no_project():
    server.current_project = None
    assert "No project loaded" in update_native_status(SCENE_UUID, "To Do")


def test_list_native_statuses_returns_labels(temp_project_server):
    result = list_native_statuses()
    assert "First Draft" in result
    assert "To Do" in result
    assert "No Status" not in result


def test_update_native_status_success(temp_project_server):
    result = update_native_status(SCENE_UUID, "Done")
    assert "Done" in result
    assert "error" not in result.lower()


def test_update_native_status_unknown_label(temp_project_server):
    result = update_native_status(SCENE_UUID, "Nonexistent")
    assert "error" in result.lower() or "not found" in result.lower()


def test_update_native_status_persists_to_scrivx(temp_project_server):
    update_native_status(SCENE_UUID, "Revised Draft")
    # Reload project and check
    set_project_path(str(temp_project_server))
    assert server.current_project.get_native_status(SCENE_UUID) == "Revised Draft"


def test_update_native_status_triggers_registry_rebuild(temp_project_server):
    update_native_status(SCENE_UUID, "To Do")
    registry_path = temp_project_server / ".ai-assistant" / "scene_registry.json"
    assert registry_path.exists()
    data = json.loads(registry_path.read_text())
    scenes_by_uuid = {s["uuid"]: s for s in data["scenes"]}
    assert scenes_by_uuid[SCENE_UUID]["status"] == "To Do"


def test_registry_status_field_present_after_rebuild(temp_project_server):
    rebuild_scene_registry()
    registry_path = temp_project_server / ".ai-assistant" / "scene_registry.json"
    data = json.loads(registry_path.read_text())
    for scene in data["scenes"]:
        assert "status" in scene
