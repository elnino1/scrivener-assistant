import pytest
from server import set_project_path, get_binder_structure, current_project
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_SCRIV = FIXTURES_DIR / "sample.scriv"

def test_get_binder_structure():
    # Setup project
    set_project_path(str(SAMPLE_SCRIV))
    
    # Check tool output
    structure_json = get_binder_structure()
    assert "Manuscript" in structure_json
    assert "\"type\": \"DraftFolder\"" in structure_json
    
    # Basic structural check
    import json
    data = json.loads(structure_json)
    assert "binder" in data
    assert len(data["binder"]) > 0

def test_get_binder_structure_no_project():
    # Reset global state (hack for testing module level global)
    import server
    server.current_project = None
    
    result = get_binder_structure()
    assert "No project loaded" in result
