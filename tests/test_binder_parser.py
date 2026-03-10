import pytest
from pathlib import Path
from scrivener_assistant.binder_parser import parse_scrivx, BinderNode

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_SCRIV = FIXTURES_DIR / "sample.scriv"
SAMPLE_SCRIVX = SAMPLE_SCRIV / "project.scrivx"

def test_parse_valid_scrivx():
    nodes = parse_scrivx(SAMPLE_SCRIVX)
    
    assert len(nodes) > 0
    
    # Check "Manuscript" (DraftFolder)
    manuscript = next((n for n in nodes if n.type == "DraftFolder"), None)
    assert manuscript is not None
    assert manuscript.title == "Manuscript"
    assert len(manuscript.children) > 0
    
    # Check nested "Chapter" -> "Scene"
    chapter = next((n for n in manuscript.children if n.title == "Chapter"), None)
    assert chapter is not None
    assert chapter.type == "Folder"
    
    scene = next((n for n in chapter.children if n.title == "Scene"), None)
    assert scene is not None
    assert scene.type == "Text"

def test_parse_missing_file():
    with pytest.raises(FileNotFoundError):
        parse_scrivx(Path("/non/existent/project.scrivx"))

def test_serialization():
    node = BinderNode(uuid="123", title="Test", type="Text")
    child = BinderNode(uuid="456", title="Child", type="Text")
    node.children.append(child)
    
    data = node.to_dict()
    assert data["uuid"] == "123"
    assert data["children"][0]["uuid"] == "456"
