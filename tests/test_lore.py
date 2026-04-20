
import pytest
import shutil
from pathlib import Path
from scrivener_assistant.project import ScrivenerProject
from scrivener_assistant.config import ProjectConfig

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_SCRIV = FIXTURES_DIR / "sample.scriv"

@pytest.fixture
def temp_project(tmp_path):
    """
    Creates a temporary copy of the sample project.
    """
    dest = tmp_path / "temp.scriv"
    shutil.copytree(SAMPLE_SCRIV, dest)
    return dest

def test_character_management(temp_project):
    config = ProjectConfig()
    project = ScrivenerProject(str(temp_project), config)
    
    # 1. Save a character
    gandalf_bio = "# Gandalf\nA wizard is never late."
    path = project.save_character("Gandalf", gandalf_bio)
    assert "Gandalf.md" in path
    assert (temp_project / f"{config.assistant_folder}/characters/Gandalf.md").exists()
    
    # 2. Get character
    content = project.get_character("Gandalf")
    assert content == gandalf_bio
    
    # 3. List characters
    chars = project.list_characters()
    assert "Gandalf" in chars
    
    # 4. Update character
    new_bio = "# Gandalf the White\nStill not late."
    project.save_character("Gandalf", new_bio)
    content = project.get_character("Gandalf")
    assert content == new_bio

def test_location_management(temp_project):
    config = ProjectConfig()
    project = ScrivenerProject(str(temp_project), config)
    
    # 1. Save location
    rivendell_desc = "# Rivendell\nThe last homely house."
    path = project.save_location("Rivendell", rivendell_desc)
    assert "Rivendell.md" in path
    
    # 2. List locations
    locs = project.list_locations()
    assert "Rivendell" in locs
    
    # 3. Get location
    content = project.get_location("Rivendell")
    assert content == rivendell_desc

def test_persistence(temp_project):
    """Ensure data persists across project re-instantiation"""
    config = ProjectConfig()
    
    # Instance 1: Save
    project1 = ScrivenerProject(str(temp_project), config)
    project1.save_character("Frodo", "Ring bearer")
    
    # Instance 2: Load
    project2 = ScrivenerProject(str(temp_project), config)
    assert project2.get_character("Frodo") == "Ring bearer"
    assert "Frodo" in project2.list_characters()
