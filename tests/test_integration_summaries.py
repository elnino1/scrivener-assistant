import pytest
import shutil
from pathlib import Path
import server
from server import save_summary, get_summary, set_project_path

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_SCRIV = FIXTURES_DIR / "sample.scriv"

@pytest.fixture
def temp_project_summaries(tmp_path):
    """
    Sets up the server with a temporary project copy.
    """
    dest = tmp_path / "temp_summaries.scriv"
    shutil.copytree(SAMPLE_SCRIV, dest)
    
    # Initialize server with this path
    set_project_path(str(dest))
    return dest

def test_summary_workflow(temp_project_summaries):
    # UUID for "Chapter"
    uuid = "FD75AC3C-F304-4EA6-ADCC-2C32D6589969"
    
    # 1. Save
    res_save = save_summary(uuid, "This is a summary of the chapter.")
    assert "Saved summary" in res_save
    
    # Verify file exists on disk
    # Expect clean name from UUID (cleaning logic removes dashes? let's check manager logic)
    # Manager logic: "".join(c for c in uuid if c.isalnum() or c in ('-',)) -> Keeps dashes
    safe_name = uuid
    summary_file = temp_project_summaries / ".ai-assistant" / "summaries" / f"{safe_name}.md"
    assert summary_file.exists()
    assert summary_file.read_text() == "This is a summary of the chapter."
    
    # 2. Get
    res_get = get_summary(uuid)
    assert res_get == "This is a summary of the chapter."
    
def test_get_summary_not_found(temp_project_summaries):
    res = get_summary("non_existent_uuid")
    assert "not found" in res
