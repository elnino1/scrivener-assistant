import pytest
from pathlib import Path
from scrivener_assistant import ScrivenerProject
from scrivener_assistant.content_parser import get_content_path, get_notes_path

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_SCRIV = FIXTURES_DIR / "sample.scriv"

# Pick a UUID we know has content from ls -R output
# tests/fixtures/sample.scriv/Files/Data/21506607-96CA-4FB1-8B5F-A1859F4DCEDE/content.rtf
VALID_UUID = "21506607-96CA-4FB1-8B5F-A1859F4DCEDE"
MISSING_UUID = "00000000-0000-0000-0000-000000000000"

def test_get_content_path_valid():
    path = get_content_path(SAMPLE_SCRIV, VALID_UUID)
    assert path is not None
    assert path.exists()
    assert path.name == "content.rtf"
    assert str(path).endswith(f"{VALID_UUID}/content.rtf")

def test_get_content_path_missing():
    path = get_content_path(SAMPLE_SCRIV, MISSING_UUID)
    assert path is None

def test_get_notes_path_valid():
    # 21506607 has both content.rtf and notes.rtf in the fixture
    path = get_notes_path(SAMPLE_SCRIV, VALID_UUID)
    assert path is not None
    assert path.exists()
    assert path.name == "notes.rtf"
    assert str(path).endswith(f"{VALID_UUID}/notes.rtf")

def test_get_notes_path_missing():
    path = get_notes_path(SAMPLE_SCRIV, MISSING_UUID)
    assert path is None

def test_get_notes_path_no_notes():
    # 87D59B4E has only content.rtf, no notes.rtf
    UUID_NO_NOTES = "87D59B4E-F1D6-4025-9FBA-33F60ED8F985"
    path = get_notes_path(SAMPLE_SCRIV, UUID_NO_NOTES)
    assert path is None

def test_project_integration():
    project = ScrivenerProject(str(SAMPLE_SCRIV))
    path = project.get_document_path(VALID_UUID)
    assert path is not None
    assert path.exists()
