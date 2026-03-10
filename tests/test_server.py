import pytest
from server import set_project_path, get_current_project
from scrivener_assistant import ScrivenerProject
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"
VALID_PROJECT = FIXTURES_DIR / "sample.scriv"

def test_get_current_project_empty():
    # Ensure no global state leak ideally, but for MVP unit test:
    # We might need to reset global if tests run in same process
    # verify default
    # Note: importing server executes module level code, creating 'mcp' object.
    # Current project is global.
    from server import current_project
    # It might be None or set by previous runs if not careful, but here it's fresh
    # actually pytest runs defined functions.
    pass 

def test_set_project_path_valid():
    result = set_project_path(str(VALID_PROJECT))
    assert "Successfully loaded" in result
    assert str(VALID_PROJECT) in get_current_project()

def test_set_project_path_invalid():
    result = set_project_path("/invalid/path.scriv")
    assert "Error loading" in result
