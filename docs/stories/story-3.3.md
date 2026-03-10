# Story 3.3: Tool: Prompt Library (Save/Load)

## Status
Done

## Story
**As a** User/AI,
**I want** to save and retrieve reusable prompts (like "Analyze Chapter"),
**so that** I don't have to retype complex instructions for every document.

## Acceptance Criteria
1.  **Storage:** Prompts are saved in `{project.scriv}/.ai-assistant/prompts/`.
2.  **Format:** Simple text or markdown files (`{name}.md` or `{name}.txt`).
3.  **Tools:**
    *   `save_prompt(name, content)`: Saves a prompt. Overwrites if exists? (Maybe fail or flag).
    *   `get_prompt(name)`: Retrieves content.
    *   `list_prompts()`: Returns list of available prompt names.
4.  **Integration:** Works relative to the currently loaded project path.

## Tasks / Subtasks
- [x] Implement PromptManager
    - [x] Create `src/scrivener_reader/prompt_manager.py` (or add to project.py if simple).
    - [x] Logic to ensure directory exists.
    - [x] Read/Write logic.
- [x] Integrate with ScrivenerProject
    - [x] Add methods to `ScrivenerProject`.
- [x] Expose MCP Tools
    - [x] `save_prompt`, `get_prompt`, `list_prompts` in `server.py`.
- [x] Test Prompt Library
    - [x] Integration test with temp project.

## Dev Notes
We can make `PromptManager` a simple helper class or just methods on `ScrivenerProject`. Given the "Coding Standards" prefer dedicated modules, let's make `src/scrivener_reader/prompt_manager.py`.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2026-01-22 | 1.0 | Initial Draft | Dev Agent |
