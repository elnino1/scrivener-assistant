# Story 1.1: Project Setup & Connection

## Status
Done

## Story
**As a** User,
**I want** to start the MCP server pointing to my Scrivener project,
**so that** the AI can access my files.

## Acceptance Criteria
1. Server starts successfully using `mcp` SDK.
2. Accepts a command-line argument or config for the `.scriv` file path.
3. Validates that the path exists and is a directory.

## Tasks / Subtasks
- [x] Initialize Python Project Structure
    - [x] Create `pyproject.toml` with dependencies (`mcp`, `pytest`)
    - [x] Create `src/server.py` entry point
    - [x] Create `src/scrivener_reader/__init__.py` and empty modules
- [x] Implement Server Entry Point
    - [x] Parse command line arguments for project path
    - [x] Initialize MCP server instance
- [x] Implement Project Path Validation
    - [x] Create `ScrivenerProject` class in `scrivener_reader/__init__.py`
    - [x] Add logic to check valid `.scriv` directory
    - [x] Handle invalid paths gracefully
- [x] Test Project Setup
    - [x] Create `tests/fixtures/sample.scriv` (mock folder)
    - [x] Write unit tests for path validation
    - [x] Write integration test for server startup

## Dev Notes
**Architecture Reference:**
- **Style:** Monolithic Python Package
- **Core Components:** `server.py`, `scrivener_reader` package
- **Tech Stack:** Python 3.10+, `mcp` SDK
- **Testing:** `pytest`

**Testing Standards:**
- **Framework:** `pytest`
- **Location:** `tests/`
- **Pattern:** AAA (Arrange, Act, Assert)

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2026-01-21 | 1.0 | Initial Draft | Dev Agent |

## Dev Agent Record
### Agent Model Used
Gemini 2.0 Flash

### Debug Log References
- Test run: d9776150-78b3-436c-969b-ff64b2cfe24a (Passed)

### Completion Notes List
- Implemented `ScrivenerProject` with validation.
- Implemented `server.py` using `FastMCP`.
- Added `set_project_path` tool.
- Verified with unit tests.

### File List
- pyproject.toml
- src/server.py
- src/scrivener_reader/__init__.py
- tests/test_project_validation.py
- tests/test_server.py
