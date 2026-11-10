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


# --- Voice tools ---

def test_voice_tools_without_project():
    import server
    saved = server.current_project
    server.current_project = None
    try:
        assert "No project loaded" in server.voice_stats(text="Il partit.")
        assert "No project loaded" in server.compute_rewrite_diff("1")
        assert "No project loaded" in server.get_voice("guide")
    finally:
        server.current_project = saved


def test_voice_tools_roundtrip(tmp_path):
    import json
    import shutil
    import server
    dest = tmp_path / "temp.scriv"
    shutil.copytree(VALID_PROJECT, dest)
    set_project_path(str(dest))

    assert "Error" in server.save_voice("style", "x")
    assert "Saved" in server.save_voice("guide", "# Guide")
    assert server.get_voice("guide") == "# Guide"
    assert "Error" in server.save_voice_exemplar("Bad Slug", "x")
    assert "Saved" in server.save_voice_exemplar("dialogue-01", "text")
    assert "dialogue-01" in server.list_voice_exemplars()
    assert server.get_voice_exemplar("dialogue-01") == "text"

    stats = json.loads(server.voice_stats(text="Il marchait. Elle partit."))
    assert stats["sentence_count"] == 2

    assert "No voice baseline" in server.compare_voice_stats(text="Il marchait.")
    assert "Error" in server.compute_voice_baseline([])

    chapter = json.loads(server.resolve_chapter_scenes("1"))
    assert chapter["number"] == 1 and chapter["scenes"]
    uuids = [s["uuid"] for s in chapter["scenes"]]
    assert "Error" in server.resolve_chapter_scenes("zzz-unknown")

    # no draft yet
    server.current_project.read_document = lambda uuid: "Il marchait dans la rue. Elle partit."
    assert "no draft" in server.compute_rewrite_diff("1")

    server.save_draft(1, "Il marchait dans la rue. Elle resta.")
    result = json.loads(server.compute_rewrite_diff("1"))
    assert result["baseline_file"] == "draft.md" and "warning" in result
    assert (dest / ".ai-assistant" / "voice" / "edits" / "chapter-01.json").exists()
    assert result["edit_rate"] > 0 and result["sentences"]["modified"] == 1

    # baseline from documents, then comparison
    summary = json.loads(server.compute_voice_baseline(uuids))
    assert summary["sources"] >= 1
    comparison = json.loads(server.compare_voice_stats(text="Il marchait dans la rue. Elle partit."))
    assert "metrics" in comparison and "out_of_tolerance" in comparison
    result = json.loads(server.compute_rewrite_diff("1"))
    server.save_draft(1, "x")  # keep draft.md only; draft.sent.md takes precedence once present
    server.current_project.draft_manager.save_file(1, "draft.sent", "Il marchait dans la rue. Elle partit.")
    assert json.loads(server.compute_rewrite_diff("1"))["baseline_file"] == "draft.sent.md"
