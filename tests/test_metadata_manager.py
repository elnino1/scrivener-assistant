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
