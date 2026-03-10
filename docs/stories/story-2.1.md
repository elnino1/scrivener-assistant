# Story 2.1: Map UUID to File

## Status
Done

## Story
**As a** System,
**I want** to map a binder UUID to the physical `.rtf` file on disk,
**so that** I can read it.

## Acceptance Criteria
1. Logic to find the numbered `content.rtf` file inside `Files/Data/{UUID}/`.
2. Handle cases where the file might be missing (empty document).
3. Verify file exists before attempting to read.

## Tasks / Subtasks
- [x] Implement Content Parser Module
    - [x] Create `src/scrivener_reader/content_parser.py`
    - [x] Implement `get_content_path(project_path, uuid)` function
- [x] Integrate with ScrivenerProject
    - [x] Add `get_document_path(uuid)` method to `ScrivenerProject`
- [x] Test Content Mapping
    - [x] Test locating valid content.rtf in fixture
    - [x] Test handling of missing/empty content
    - [x] Verify paths are absolute and secure

## Dev Notes
**Technical Detail:**
- Scrivener 3 stores content in `Files/Data/{UUID}/content.rtf`.
- Some UUID folders might not exist if the item has no content (e.g., pure folder).
- Some UUID folders might exist but contain no `content.rtf` (e.g. only `synopsis.txt`).

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2026-01-22 | 1.0 | Initial Draft | Dev Agent |

## Dev Agent Record
### Agent Model Used
To be populated

### Debug Log References
To be populated

### Completion Notes List
To be populated

### File List
To be populated
