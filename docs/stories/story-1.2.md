# Story 1.2: Parse Binder Structure

## Status
Done

## Story
**As a** System,
**I want** to parse the `.scrivx` XML file,
**so that** I can understand the hierarchy of the project.

## Acceptance Criteria
1. locate the `.scrivx` file within the `.scriv` directory.
2. Parse the XML to build a tree of UUIDs and Titles.
3. Handle nesting (folders within folders).

## Tasks / Subtasks
- [x] Implement Binder Node Models
    - [x] Define `BinderNode` data class (uuid, title, type, children)
- [x] Implement Scrivx Parsing Logic
    - [x] Create `src/scrivener_reader/binder_parser.py`
    - [x] Implement `parse_scrivx(path)` using `xml.etree`
    - [x] Handle recursive `BinderItem` parsing
- [x] Integrate with ScrivenerProject
    - [x] Update `ScrivenerProject` to call parser on init
    - [x] Expose `get_binder_structure()` method
- [x] Test Binder Parsing
    - [x] Update `tests/fixtures/sample.scriv` with realistic `.scrivx` content
    - [x] Write unit tests for nested structures
    - [x] Write integration test ensuring server returns correct JSON

## Dev Notes
**Architecture Reference:**
- **Parsing:** `xml.etree.ElementTree`
- **Data Model:** `BinderNode` (Recursive)

**Technical Approach:**
- Scrivener 3 XML structure usually has a `<Binder>` root with `<BinderItem>` elements.
- `BinderItem` has `UUID`, `Type`, and `<Title>`.
- Children are nested within `<Children>` tags inside `BinderItem`.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2026-01-21 | 1.0 | Initial Draft | Dev Agent |

## Dev Agent Record
### Agent Model Used
To be populated

### Debug Log References
To be populated

### Completion Notes List
To be populated

### File List
To be populated
