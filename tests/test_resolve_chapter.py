import json

import pytest

from scrivener_assistant.config import ProjectConfig
from scrivener_assistant.scene_registry_manager import SceneRegistryManager


def _scene(uuid, title, path, words=100):
    return {"uuid": uuid, "title": title, "binder_path": path, "word_count": words}


@pytest.fixture
def mgr(tmp_path):
    m = SceneRegistryManager(tmp_path, ProjectConfig())
    scenes = [
        _scene("U1", "Section 1", ["Manuscrit", "Celestia", "Section 1"], 10),
        _scene("U2", "Section 2", ["Manuscrit", "Celestia", "Section 2"], 20),
        _scene("U3", "Rencontre", ["Manuscrit", "La découverte de Vee", "Rencontre"], 30),
        _scene("U4", "Épilogue", ["Manuscrit", "Épilogue"], 40),
        _scene("U5", "Lune", ["Manuscrit", "La lune rousse", "Sub", "Lune"], 50),
    ]
    m.registry_path.parent.mkdir(parents=True)
    m.registry_path.write_text(json.dumps({"scenes": scenes}), encoding="utf-8")
    return m


def test_by_number(mgr):
    r = mgr.resolve_chapter("1", None)
    assert r["number"] == 1 and r["title"] == "Celestia"
    assert [s["uuid"] for s in r["scenes"]] == ["U1", "U2"]
    assert r["scenes"][0] == {"uuid": "U1", "title": "Section 1", "word_count": 10}


def test_nested_scenes_grouped(mgr):
    r = mgr.resolve_chapter("4", None)
    assert r["title"] == "La lune rousse" and [s["uuid"] for s in r["scenes"]] == ["U5"]


def test_chapter_that_is_a_text_document(mgr):
    r = mgr.resolve_chapter("3", None)
    assert r["title"] == "Épilogue" and [s["uuid"] for s in r["scenes"]] == ["U4"]


def test_by_title_accent_and_case_insensitive(mgr):
    assert mgr.resolve_chapter("epilogue", None)["number"] == 3
    assert mgr.resolve_chapter("LA DECOUVERTE DE VEE", None)["number"] == 2


def test_unique_prefix(mgr):
    assert mgr.resolve_chapter("cel", None)["number"] == 1


def test_ambiguous_prefix(mgr):
    with pytest.raises(ValueError, match="ambiguous"):
        mgr.resolve_chapter("la ", None)


def test_not_found(mgr):
    with pytest.raises(ValueError, match="not found"):
        mgr.resolve_chapter("Inconnu", None)
    with pytest.raises(ValueError, match="not found"):
        mgr.resolve_chapter("9", None)
    with pytest.raises(ValueError, match="not found"):
        mgr.resolve_chapter("0", None)
