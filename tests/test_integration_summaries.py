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
    uuid = "87D59B4E-F1D6-4025-9FBA-33F60ED8F985"
    
    # 1. Save
    res_save = save_summary(uuid, "This is a summary of the chapter.")
    assert "Saved summary" in res_save
    
    # Verify file exists on disk
    short_uuid = uuid.split('-')[0]
    summary_files = list((temp_project_summaries / ".ai-assistant" / "summaries").rglob(f"*{short_uuid}*.md"))
    assert len(summary_files) > 0, "Summary file should exist"
    summary_file = summary_files[0]
    assert summary_file.read_text() == "This is a summary of the chapter."
    
    # 2. Get
    res_get = get_summary(uuid)
    assert res_get == "This is a summary of the chapter."
    
def test_get_summary_not_found(temp_project_summaries):
    res = get_summary("non_existent_uuid")
    assert "not found" in res
