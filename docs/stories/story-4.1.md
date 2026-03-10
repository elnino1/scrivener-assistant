# Story 4.1: Summary Tools (Save/Get)

## Status
Done

## Story
**As a** User/AI,
**I want** to save and retrieve summaries of specific documents (by UUID),
**so that** I can reuse them later to reduce token usage.

## Acceptance Criteria
1.  **Storage:** Summaries are saved in `{project.scriv}/.ai-assistant/summaries/`.
2.  **Format:** Text/Markdown files named `{uuid}.md`.
3.  **Tools:**
    *   `save_summary(uuid, content)`: Saves summary text.
    *   `get_summary(uuid)`: Retrieves summary text.
4.  **Integration:** Works relative to the currently loaded project path.

## Tasks / Subtasks
- [x] Implement SummaryManager
    - [x] Create `src/scrivener_reader/summary_manager.py`.
    - [x] Implement `save_summary(uuid, content)` and `get_summary(uuid)`.
- [x] Integrate with ScrivenerProject
    - [x] Add `summary_manager` instance and methods.
- [x] Expose MCP Tools
    - [x] `save_summary`, `get_summary` in `server.py`.
- [x] Test Summary Tools
    - [x] Integration test with temp project.

## Dev Notes
Very similar logic to PromptManager, just different folder and naming convention (UUID based).

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2026-01-22 | 1.0 | Initial Draft | Dev Agent |
