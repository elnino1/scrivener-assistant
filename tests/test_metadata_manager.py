import pytest
import shutil
from pathlib import Path
from scrivener_assistant.metadata_manager import MetadataManager
import xml.etree.ElementTree as ET

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_SCRIV = FIXTURES_DIR / "sample.scriv"

@pytest.fixture
def temp_project(tmp_path):
    """
    Creates a temporary copy of the sample project to safely test writing.
    """
    dest = tmp_path / "temp.scriv"
    shutil.copytree(SAMPLE_SCRIV, dest)
    return dest

def test_metadata_manager_loads(temp_project):
    scrivx = list(temp_project.glob("*.scrivx"))[0]
    manager = MetadataManager(scrivx)
    assert manager.root.tag == "ScrivenerProject"

def test_ensure_field_definition(temp_project):
    scrivx = list(temp_project.glob("*.scrivx"))[0]
    manager = MetadataManager(scrivx)
    
    # Test creating new field
    field_id = manager.ensure_field_definition("Philosophy")
    assert field_id == "Custom:Philosophy"
    
    # Verify XML structure
    settings = manager.root.find("CustomMetaDataSettings")
    assert settings is not None
    field = settings.find(f"MetaDataField[@ID='{field_id}']")
    assert field is not None
    assert field.text == "Philosophy"
    
    # Test reusing existing
    field_id_2 = manager.ensure_field_definition("Philosophy")
    assert field_id_2 == field_id

def test_update_metadata_value(temp_project):
    scrivx = list(temp_project.glob("*.scrivx"))[0]
    manager = MetadataManager(scrivx)
    
    # UUID from fixture: 21506607-96CA-4FB1-8B5F-A1859F4DCEDE (Copyright)
    uuid = "21506607-96CA-4FB1-8B5F-A1859F4DCEDE"
    
    manager.update_metadata(uuid, "PlotSummary", "A crucial scene.")
    
    # Verify in memory
    item = manager.root.find(f".//BinderItem[@UUID='{uuid}']")
    meta_item = item.find(".//MetaData/CustomMetaData/MetaDataItem")
    assert meta_item is not None
    assert meta_item.find("Value").text == "A crucial scene."

def test_get_custom_metadata_empty(temp_project):
    scrivx = list(temp_project.glob("*.scrivx"))[0]
    manager = MetadataManager(scrivx)
    uuid = "21506607-96CA-4FB1-8B5F-A1859F4DCEDE"  # Copyright — no custom metadata yet
    assert manager.get_custom_metadata(uuid) == {}

def test_get_custom_metadata_returns_values(temp_project):
    scrivx = list(temp_project.glob("*.scrivx"))[0]
    manager = MetadataManager(scrivx)
    uuid = "21506607-96CA-4FB1-8B5F-A1859F4DCEDE"

    manager.update_metadata(uuid, "Status", "Draft")
    manager.update_metadata(uuid, "POV", "Alice")

    result = manager.get_custom_metadata(uuid)
    assert result == {"Status": "Draft", "POV": "Alice"}

def test_list_native_statuses_returns_labels(temp_project):
    scrivx = list(temp_project.glob("*.scrivx"))[0]
    manager = MetadataManager(scrivx)
    statuses = manager.list_native_statuses()
    assert "First Draft" in statuses
    assert "To Do" in statuses
    assert "No Status" not in statuses  # sentinel value, excluded

def test_get_native_status_resolves_id(temp_project):
    scrivx = list(temp_project.glob("*.scrivx"))[0]
    manager = MetadataManager(scrivx)
    uuid = "0A7EDD9F-9DE0-4CC9-9AC1-EE0E3769B6A8"  # Scene — has <StatusID>2</StatusID>
    assert manager.get_native_status(uuid) == "First Draft"

def test_get_native_status_returns_none_when_absent(temp_project):
    scrivx = list(temp_project.glob("*.scrivx"))[0]
    manager = MetadataManager(scrivx)
    uuid = "21506607-96CA-4FB1-8B5F-A1859F4DCEDE"  # Copyright — no StatusID
    assert manager.get_native_status(uuid) is None

def test_set_native_status_writes_correct_id(temp_project):
    scrivx = list(temp_project.glob("*.scrivx"))[0]
    manager = MetadataManager(scrivx)
    uuid = "21506607-96CA-4FB1-8B5F-A1859F4DCEDE"

    manager.set_native_status(uuid, "To Do")

    item = manager.root.find(f".//BinderItem[@UUID='{uuid}']")
    status_id = item.find("MetaData/StatusID")
    assert status_id is not None
    assert status_id.text == "1"  # "To Do" maps to ID 1 in the fixture

def test_set_native_status_raises_on_unknown_label(temp_project):
    scrivx = list(temp_project.glob("*.scrivx"))[0]
    manager = MetadataManager(scrivx)
    with pytest.raises(ValueError, match="not found"):
        manager.set_native_status("21506607-96CA-4FB1-8B5F-A1859F4DCEDE", "Nonexistent Status")

def test_set_native_status_overwrites_existing(temp_project):
    scrivx = list(temp_project.glob("*.scrivx"))[0]
    manager = MetadataManager(scrivx)
    uuid = "0A7EDD9F-9DE0-4CC9-9AC1-EE0E3769B6A8"  # already has StatusID 2

    manager.set_native_status(uuid, "Done")

    assert manager.get_native_status(uuid) == "Done"

def test_rolling_backup(temp_project):
    scrivx = list(temp_project.glob("*.scrivx"))[0]
    manager = MetadataManager(scrivx)
    
    # 1st Save
    manager.save()
    assert (scrivx.parent / f"{scrivx.name}.bak.1").exists()
    
    # 2nd Save
    manager.save()
    assert (scrivx.parent / f"{scrivx.name}.bak.1").exists()
    assert (scrivx.parent / f"{scrivx.name}.bak.2").exists()
