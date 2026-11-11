import pytest

from scrivener_assistant.config import ProjectConfig
from scrivener_assistant.voice_manager import VoiceManager


@pytest.fixture
def mgr(tmp_path):
    return VoiceManager(tmp_path, ProjectConfig())


def test_base_dir(tmp_path, mgr):
    assert mgr.base_dir == tmp_path / ".ai-assistant" / "voice"


def test_save_and_get_file(mgr):
    assert mgr.get_file("guide") is None
    mgr.save_file("guide", "# Guide")
    assert mgr.get_file("guide") == "# Guide"


@pytest.mark.parametrize("name", ["style", "../guide", "baseline", ""])
def test_invalid_file_name(mgr, name):
    with pytest.raises(ValueError):
        mgr.save_file(name, "x")
    with pytest.raises(ValueError):
        mgr.get_file(name)


def test_baseline_roundtrip(mgr):
    assert mgr.get_baseline() is None
    mgr.save_baseline({"sources": 2, "métrique": 1.5})
    assert mgr.get_baseline() == {"sources": 2, "métrique": 1.5}


def test_exemplars(mgr):
    assert mgr.list_exemplars() == []
    mgr.save_exemplar("dialogue-01", "text")
    mgr.save_exemplar("action-02", "text2")
    assert mgr.list_exemplars() == ["action-02", "dialogue-01"]
    assert mgr.get_exemplar("dialogue-01") == "text"
    assert mgr.get_exemplar("missing") is None


@pytest.mark.parametrize("slug", ["../x", "Dialogue", "a b", "a/b", "", "é"])
def test_invalid_slug(mgr, slug):
    with pytest.raises(ValueError):
        mgr.save_exemplar(slug, "x")
    with pytest.raises(ValueError):
        mgr.get_exemplar(slug)


def test_edits_roundtrip(mgr):
    assert mgr.get_edits(3) is None
    path = mgr.save_edits(3, {"edit_rate": 0.2})
    assert path.name == "chapter-03.json"
    assert mgr.get_edits(3) == {"edit_rate": 0.2}
