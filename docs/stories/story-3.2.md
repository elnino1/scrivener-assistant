# Story 3.2: Tool: Update Metadata

## Status
Done

## Story
**As a** AI,
**I want** to call `update_metadata(uuid, field, value)`,
**so that** I can save my analysis results directly into the Scrivener project.

## Acceptance Criteria
1.  **Expose Tool:** `update_metadata` available in MCP server.
2.  **Arguments:** Accepts UUID, Field Name, and Value.
3.  **Error Handling:** gracefully handles invalid UUIDs or write errors.
4.  **Verification:** Returns a success message confirming the update.

## Tasks / Subtasks
- [x] Expose MCP Tool
    - [x] Update `src/server.py` with `update_metadata` function.
- [x] Test Tool Integration
    - [x] Create `tests/test_integration_metadata.py`.
    - [x] Verify tool call successfully modifies the XML (using temp project).

## Dev Notes
The tool should wrap `current_project.update_metadata()`.
Since this modifies state, we must ensure we don't run this on the main sample fixture in a way that pollutes it for other tests (though the manager uses `.bak` files, modifying the git-tracked fixture is bad practice).
**Test Strategy:** The integration test MUST use a temporary copy of the project, similar to `test_metadata_manager.py`.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2026-01-22 | 1.0 | Initial Draft | Dev Agent |
