import pytest
import shutil
from pathlib import Path
import server
from server import update_metadata, set_project_path

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_SCRIV = FIXTURES_DIR / "sample.scriv"

@pytest.fixture
def temp_project_server(tmp_path):
    """
    Sets up the server with a temporary project copy.
    """
    dest = tmp_path / "temp_server.scriv"
    shutil.copytree(SAMPLE_SCRIV, dest)
    
    # Initialize server with this path
    set_project_path(str(dest))
    return dest

def test_update_metadata_tool_success(temp_project_server):
    uuid = "21506607-96CA-4FB1-8B5F-A1859F4DCEDE" # Copyright
    
    # Call tool
    result = update_metadata(uuid, "ReviewStatus", "Approved")
    
    assert "Successfully updated" in result
    
    # Verify persistence
    # (In a real scenario we might re-read the file, but here we trust the manager tests cover the writing part.
    # We mainly verify the tool didn't crash and returned success)
    
    # Optional: Verify backup creation
    assert (temp_project_server / "project.scrivx.bak.1").exists()

def test_update_metadata_tool_no_project():
    server.current_project = None
    result = update_metadata("any-id", "Field", "Value")
    assert "No project loaded" in result

def test_update_metadata_tool_bad_uuid(temp_project_server):
    result = update_metadata("bad-uuid", "Field", "Value")
    assert "Error updating metadata" in result
