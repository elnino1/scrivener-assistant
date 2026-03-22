import pytest
from server import set_project_path, read_document, read_document_notes
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_SCRIV = FIXTURES_DIR / "sample.scriv"

# Known UUID from fixture having content
# tests/fixtures/sample.scriv/Files/Data/21506607-96CA-4FB1-8B5F-A1859F4DCEDE/content.rtf
# That is "Copyright" document in .scrivx
VALID_UUID = "21506607-96CA-4FB1-8B5F-A1859F4DCEDE"

def test_read_document_success():
    set_project_path(str(SAMPLE_SCRIV))
    
    # We don't control the fixture content exactly (since it's copied from real files),
    # but we can check it returns *something* non-empty
    content = read_document(VALID_UUID)
    assert content != ""
    assert "Error" not in content

def test_read_document_missing_id():
    set_project_path(str(SAMPLE_SCRIV))
    # Fake ID
    content = read_document("FAKE-UUID-123")
    assert content == "" # logic says return empty string if no content

def test_read_document_no_project():
    import server
    server.current_project = None
    assert "No project loaded" in read_document(VALID_UUID)

# Notes — 21506607 has notes.rtf in the fixture
def test_read_document_notes_success():
    set_project_path(str(SAMPLE_SCRIV))
    notes = read_document_notes(VALID_UUID)
    assert notes != ""
    assert "Error" not in notes

def test_read_document_notes_missing_id():
    set_project_path(str(SAMPLE_SCRIV))
    notes = read_document_notes("FAKE-UUID-123")
    assert notes == ""

def test_read_document_notes_no_notes_file():
    set_project_path(str(SAMPLE_SCRIV))
    # 87D59B4E has content.rtf but no notes.rtf
    notes = read_document_notes("87D59B4E-F1D6-4025-9FBA-33F60ED8F985")
    assert notes == ""

def test_read_document_notes_no_project():
    import server
    server.current_project = None
    assert "No project loaded" in read_document_notes(VALID_UUID)
