# Story 3.1: Metadata Infrastructure (Read/Write)

## Status
Done

## Story
**As a** System,
**I want** to parse and modify the `.scrivx` XML to handle Custom Metadata,
**so that** I can store structured analysis data from the AI.

## Acceptance Criteria
1.  **Safety:** Implement rolling backups (`.bak.1` to `.bak.5`) before writing.
2.  **Field Definition:** Capability to check if a Custom Metadata Field (e.g., "Philosophy") exists, and create it if not.
3.  **Value Update:** Capability to find a specific BinderItem by UUID and update/insert its Custom Metadata value.
4.  **Persistence:** Changes are correctly saved to the XML file.

## Tasks / Subtasks
- [x] Implement Metadata Manager
    - [x] Create `src/scrivener_reader/metadata_manager.py`
    - [x] Implement `__init__` (load XML) and `save` (write with backup)
    - [x] Implement `ensure_field_definition(name, type)`
    - [x] Implement `update_metadata_value(uuid, field_name, value)`
- [x] Integrate with ScrivenerProject
    - [x] Extend `ScrivenerProject` to use `MetadataManager`
- [x] Test Metadata Logic
    - [x] Test XML loading/saving (mocked filesystem for safety)
    - [x] Test new field creation (verifying correct XML structure)
    - [x] Test value update for existing and new fields
    - [x] Test rolling backups

## Dev Notes
**XML Structure:**
*   Settings: `/ScrivenerProject/CustomMetaDataSettings/MetaDataField`
*   Item Values: `/ScrivenerProject/Binder//BinderItem/MetaData/CustomMetaData/MetaDataItem`

**Safe Writing:**
Use `shutil.copy2` for backup. Use `xml.etree.ElementTree.write` with `encoding='UTF-8'` and `xml_declaration=True`.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2026-01-22 | 1.0 | Initial Draft | Dev Agent |
