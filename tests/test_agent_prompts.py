import asyncio

import pytest

from scrivener_assistant.agent_prompts import load_agent_prompt


def test_load_known_prompt():
    assert "Celestia" in load_agent_prompt("voice_bootstrap")


@pytest.mark.parametrize("name", ["", "../server", "Voice_Bootstrap", "a/b", "voice-bootstrap", "nope"])
def test_load_invalid_or_unknown_name(name):
    with pytest.raises(ValueError):
        load_agent_prompt(name)


def _render(args):
    import server
    return asyncio.run(server.mcp.get_prompt("voice-bootstrap", args))


def test_voice_bootstrap_prompt_registered():
    import server
    prompts = asyncio.run(server.mcp.list_prompts())
    match = [p for p in prompts if p.name == "voice-bootstrap"]
    assert len(match) == 1
    assert [a.name for a in match[0].arguments] == ["corpus"]
    assert not match[0].arguments[0].required


def test_voice_bootstrap_prompt_renders_without_project():
    import server
    saved = server.current_project
    server.current_project = None
    try:
        result = _render({})
    finally:
        server.current_project = saved
    text = result.messages[0].content.text
    assert "Celestia" in text
    assert "remplace le corpus par défaut" not in text


def test_voice_bootstrap_prompt_corpus_override():
    text = _render({"corpus": "chapitres 3 et 4"}).messages[0].content.text
    assert "remplace le corpus par défaut" in text
    assert "chapitres 3 et 4" in text


def test_voice_learner_prompt_registered_and_renders():
    import server
    prompts = asyncio.run(server.mcp.list_prompts())
    match = [p for p in prompts if p.name == "voice-learner"]
    assert len(match) == 1
    assert [a.name for a in match[0].arguments] == ["chapter"]
    assert not match[0].arguments[0].required
    text = asyncio.run(server.mcp.get_prompt("voice-learner", {})).messages[0].content.text
    assert "save_edit_labels" in text and "Chapitre indiqué" not in text


def test_voice_learner_prompt_chapter_argument():
    import server
    text = asyncio.run(server.mcp.get_prompt("voice-learner", {"chapter": "3"})).messages[0].content.text
    assert "Chapitre indiqué par l'auteur" in text and text.rstrip().endswith("3")


def test_voice_learner_wrapper_file():
    from pathlib import Path
    wrapper = Path(__file__).parent.parent / ".claude" / "agents" / "voice-learner.md"
    assert "voice_learner.md" in wrapper.read_text(encoding="utf-8")
    assert "Celestia" not in load_agent_prompt("voice_learner")
