# Story 2.2: Read Document Content

## Status
Done

## Story
**As a** System,
**I want** to convert the internal RTF content to plain text and expose it via a tool,
**so that** the AI can read the actual writing in the project.

## Acceptance Criteria
1. Implement robust RTF stripping (using `striprtf`).
2. Strip styling but preserve paragraph breaks.
3. Expose `read_document(uuid)` MCP tool.
4. Handle requests for invalid or empty documents gracefully.

## Tasks / Subtasks
- [x] Implement RTF Converter
    - [x] Create `src/scrivener_reader/rtf_converter.py`
    - [x] Implement `convert_rtf_to_text(rtf_content: str) -> str`
- [x] Integrate with ScrivenerProject
    - [x] Add `read_document(uuid)` method to `ScrivenerProject`
    - [x] Logic: Get path -> Read file -> Convert -> Return
- [x] Expose MCP Tool
    - [x] Add `read_document` tool to `server.py`
- [x] Test content reading
    - [x] Unit test for RTF stripper (bold, italics, etc.)
    - [x] Integration test reading a known file from fixture

## Dev Notes
**Library:** `striprtf` is already in `pyproject.toml`.
**Encoding:** Scrivener RTF files are usually standard 7-bit ASCII RTF headers, but content inside handles unicode. Python's `open(..., encoding='utf-8')` might crash if RTF is pure ASCII/Latin-1. Need to handle file reading carefully (RTF spec says 7-bit ASCII for control words, but Scrivener might save as UTF-8 plaintext RTF).
*Recommendation:* Try reading as utf-8, fallback to latin-1 if needed, or rely on `striprtf` expected input.

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
