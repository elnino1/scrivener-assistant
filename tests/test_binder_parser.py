import pytest
from pathlib import Path
from scrivener_assistant.binder_parser import parse_scrivx, BinderNode, get_draft_root, get_all_text_descendants

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

def test_get_draft_root_finds_draft_folder():
    nodes = parse_scrivx(SAMPLE_SCRIVX)
    root = get_draft_root(nodes)
    assert root is not None
    assert root.type == "DraftFolder"
    assert root.title == "Manuscript"


def test_get_draft_root_returns_none_without_draft_folder():
    nodes = [
        BinderNode(uuid="A", title="Notes", type="Folder"),
        BinderNode(uuid="B", title="Research", type="ResearchFolder"),
    ]
    assert get_draft_root(nodes) is None


def test_get_all_text_descendants_returns_only_text_nodes():
    root = BinderNode(uuid="ROOT", title="Draft", type="DraftFolder")
    chapter = BinderNode(uuid="CH", title="Chapter", type="Folder")
    scene1 = BinderNode(uuid="S1", title="Scene 1", type="Text")
    scene2 = BinderNode(uuid="S2", title="Scene 2", type="Text")
    chapter.children = [scene1, scene2]
    root.children = [chapter]

    result = get_all_text_descendants(root)
    assert len(result) == 2
    assert all(n.type == "Text" for n in result)
    assert {n.uuid for n in result} == {"S1", "S2"}


def test_get_all_text_descendants_excludes_folder_nodes():
    root = BinderNode(uuid="ROOT", title="Draft", type="DraftFolder")
    folder = BinderNode(uuid="F1", title="Chapter", type="Folder")
    scene = BinderNode(uuid="T1", title="Scene", type="Text")
    folder.children = [scene]
    root.children = [folder]

    result = get_all_text_descendants(root)
    uuids = {n.uuid for n in result}
    assert "F1" not in uuids
    assert "T1" in uuids


def test_serialization():
    node = BinderNode(uuid="123", title="Test", type="Text")
    child = BinderNode(uuid="456", title="Child", type="Text")
    node.children.append(child)
    
    data = node.to_dict()
    assert data["uuid"] == "123"
    assert data["children"][0]["uuid"] == "456"
