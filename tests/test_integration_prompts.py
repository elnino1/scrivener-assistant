import pytest
import shutil
from pathlib import Path
import server
from server import save_prompt, get_prompt, list_prompts, set_project_path

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_SCRIV = FIXTURES_DIR / "sample.scriv"

@pytest.fixture
def temp_project_prompts(tmp_path):
    """
    Sets up the server with a temporary project copy.
    """
    dest = tmp_path / "temp_prompts.scriv"
    shutil.copytree(SAMPLE_SCRIV, dest)
    
    # Initialize server with this path
    set_project_path(str(dest))
    return dest

def test_prompt_workflow(temp_project_prompts):
    # 1. Save
    res_save = save_prompt("analyze_test", "Analyze this please.")
    assert "Saved prompt" in res_save
    
    # Verify file exists on disk
    prompt_file = temp_project_prompts / server.current_project.config.assistant_folder / "prompts" / "analyze_test.md"
    assert prompt_file.exists()
    assert prompt_file.read_text() == "Analyze this please."
    
    # 2. List
    res_list = list_prompts()
    assert "- analyze_test" in res_list
    
    # 3. Get
    res_get = get_prompt("analyze_test")
    assert res_get == "Analyze this please."
    
def test_get_prompt_not_found(temp_project_prompts):
    res = get_prompt("non_existent")
    assert "not found" in res

def test_save_prompt_sanitization(temp_project_prompts):
    # Should strip unsafe chars
    save_prompt("unsafe/name", "content")
    
    # Should exist as 'unsafename.md' or similar based on logic
    # My logic: "".join(c for c in name if c.isalnum() or c in (' ', '-', '_'))
    # "unsafe/name" -> "unsafename"
    
    expected_file = temp_project_prompts / server.current_project.config.assistant_folder / "prompts" / "unsafename.md"
    assert expected_file.exists()
