import pytest
import os
from pathlib import Path
from scrivener_assistant import ScrivenerProject

FIXTURES_DIR = Path(__file__).parent / "fixtures"
VALID_PROJECT = FIXTURES_DIR / "sample.scriv"

def test_valid_project_loading():
    project = ScrivenerProject(str(VALID_PROJECT))
    assert project.path == VALID_PROJECT.resolve()
    assert project.scrivx_file.name == "project.scrivx"

def test_invalid_path_not_exists():
    with pytest.raises(FileNotFoundError):
        ScrivenerProject("/non/existent/path.scriv")

def test_invalid_extension():
    # create a dummy dir without .scriv
    dummy_dir = FIXTURES_DIR / "dummy_folder"
    dummy_dir.mkdir(exist_ok=True)
    try:
        with pytest.raises(ValueError, match="must end with .scriv"):
            ScrivenerProject(str(dummy_dir))
    finally:
        dummy_dir.rmdir()

def test_missing_scrivx():
    # create a dummy .scriv without .scrivx
    bad_scriv = FIXTURES_DIR / "bad.scriv"
    bad_scriv.mkdir(exist_ok=True)
    try:
        with pytest.raises(ValueError, match="No .scrivx file found"):
            ScrivenerProject(str(bad_scriv))
    finally:
        # cleaning up logic would go here or use fixture
        bad_scriv.rmdir()
