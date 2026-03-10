# Scrivener Assistant MCP Product Requirements Document (PRD)

## Goals and Background Context
### Goals
*   Deliver a working MCP server that demonstrates the power of context-aware AI assistance for complex documents.
*   Enable AI to correctly identify the project structure (Binder).
*   Enable AI to read specific scenes/chapters without manual user copy-pasting.

### Background Context
Scrivener is the gold standard for long-form writing, but getting AI assistance on a large, multi-document project is currently fragmented. Writers have to copy-paste individual scenes into generic chat interfaces, losing the broader context. This project aims to bridge that gap by allowing AI agents to "read" the Scrivener project directly via the Model Context Protocol.

### Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2026-01-21 | 1.0 | Initial MVP PRD | PM Agent |

## Requirements
### Functional Requirements (FR)
*   **FR1 Project Connection:** The server must accept a valid path to a `.scriv` directory.
*   **FR2 Binder Structure:** The server must parse the `.scrivx` file to extract the full binder hierarchy (folders, documents) including UUIDs and titles.
*   **FR3 Content Retrieval:** The server must be able to read the content of a specific document (identified by UUID) by locating and parsing its corresponding `.rtf` file.
*   **FR4 Metadata Access:** The server must retrieve synopsis and notes for a given document.
*   **FR5 Text Conversion:** The server must convert internal RTF content to clean, plain text for LLM consumption.
*   **FR6 Metadata Writing:** The server must be able to create new custom metadata fields and populate them for specific documents.

### Non-Functional Requirements (NFR)
*   **NFR1 Privacy:** All processing must happen locally; no data sent to external non-LLM services.
*   **NFR2 Performance:** Binder parsing should take less than 2 seconds for a standard project (approx 1000 items).
*   **NFR3 Compatibility:** Must support Scrivener 3 format.

## User Interface Design Goals
*(N/A - This is a headless MCP server)*

## Technical Assumptions
*   **Language:** Python (using `mcp` SDK).
*   **Repository:** Single repository.
*   **Architecture:** Monolithic script/package.
*   **Parsing Strategy:**
    *   `xml.etree.ElementTree` for Binder (`.scrivx`).
    *   `striprtf` or `pyrtf-ng` for content (`.rtf`).
*   **Testing:** `pytest` with a sample `.scriv` fixture.

## Epic List
*   **Epic 1: Foundation & Binder Navigation:** Establish project setup, authentication, and basic user management.
*   **Epic 2: Content Extraction & Inspection:** Create and manage primary domain objects with CRUD operations.
*   **Epic 3: Metadata & Analysis:** Implement write capabilities to store analysis results (characters, plot, etc.) back into Scrivener's metadata.
*   **Epic 4: Summarization & caching:** Store chapter summaries externally to reduce context window usage.
*   **Epic 5: Style Review & Batch Analysis:** Store style feedback and enable efficient multi-task analysis.
*   **Epic 6: World Building:** Manage character and location databases to support coherence checking.

## Epic Details

### Epic 1: Foundation & Binder Navigation
**Goal:** Establish the MCP server, handle configuration (project path), and successfully parse/return the project structure (Binder) to the client.

#### Story 1.1: Project Setup & Connection
*   As a User, I want to start the MCP server pointing to my Scrivener project, so that the AI can access my files.
*   **Acceptance Criteria:**
    *   1: Server starts successfully using `mcp` SDK.
    *   2: Accepts a command-line argument or config for the `.scriv` file path.
    *   3: Validates that the path exists and is a directory.

#### Story 1.2: Parse Binder Structure
*   As a System, I want to parse the `.scrivx` XML file, so that I can understand the hierarchy of the project.
*   **Acceptance Criteria:**
    *   1: locate the `.scrivx` file within the `.scriv` directory.
    *   2: Parse the XML to build a tree of UUIDs and Titles.
    *   3: Handle nesting (folders within folders).

#### Story 1.3: Tool: Get Context
*   As an AI, I want to call `get_binder_structure`, so that I can see the outline of the book.
*   **Acceptance Criteria:**
    *   1: Expose an MCP tool `get_binder_structure`.
    *   2: Returns a JSON representation of the binder.
    *   3: Includes ID, Title, and Type (Folder/Text) for each node.

### Epic 2: Content Extraction & Inspection
**Goal:** Implement the logic to read specific documents by ID, parsing their underlying RTF files into plain text, and retrieving metadata.

#### Story 2.1: Map UUID to File
*   As a System, I want to map a binder UUID to the physical `.rtf` file on disk, so I can read it.
*   **Acceptance Criteria:**
    *   1: Logic to find the numbered `content.rtf` file inside `Files/Data/{UUID}/`.
    *   2: Handle cases where the file might be missing (empty document).

#### Story 2.2: RTF to Text Conversion
*   As a System, I want to convert RTF to Plain Text, so that the AI can read it without formatting noise.
*   **Acceptance Criteria:**
    *   1: Implement/Import a robust RTF stripper.
    *   2: Strip styling (bold/italic) but keep paragraph breaks.
    *   3: Return clean UTF-8 string.

#### Story 2.3: Tool: Read Document
*   As an AI, I want to call `read_document(uuid)`, so that I can read the text of a scene.
*   **Acceptance Criteria:**
    *   1: Expose an MCP tool `read_document`.
    *   2: Input: UUID string.
    *   3: Output: The plain text content of the document.

### Epic 3: Metadata & Analysis
**Goal:** Enable the AI to store its analysis results directly in the Scrivener project by creating and populating custom metadata fields.

#### Story 3.1: Metadata Infrastructure (Read/Write)
*   As a System, I want to parse and modify the `.scrivx` XML to handle Custom Metadata, so that I can store structured data.
*   **Acceptance Criteria:**
    *   1: Parse existing `<CustomMetaDataSettings>` and `<CustomMetaData>`.
    *   2: Logic to create a new Field Definition if it doesn't exist.
    *   3: Logic to update/insert a value for a specific Binder Item.
    *   4: Save the modified XML back to disk safely.

#### Story 3.2: Tool: Update Metadata
*   As an AI, I want to call `update_metadata(uuid, field, value)`, so that I can save my analysis.
*   **Acceptance Criteria:**
    *   1: Expose MCP tool `update_metadata`.
    *   2: Accepts UUID, Field Name, and Value.
    *   3: Automatically creates the field definition if missing.
    *   4: Updates the project file.

### Epic 4: Summarization & Caching
**Goal:** Reduce token usage by storing and retrieving summaries of documents manually generated by the AI.

#### Story 4.1: Summary Tools
*   As a User, I want to save a summary of a chapter, so that I don't have to re-read the whole text later.
*   **Acceptance Criteria:**
    *   1: Tool `save_summary(uuid, summary_text)`.
    *   2: Tool `get_summary(uuid)`.
    *   3: Stored in `.ai-assistant/summaries/{uuid}.md`.
    *   4: Graceful handling if summary doesn't exist.

### Epic 5: Style Review & Batch Analysis
**Goal:** Enable AI to provide comprehensive chapter analysis with style feedback, and optimize by performing multiple tasks in one read operation.

#### Story 5.1: Style Review Storage
*   As a User, I want to store AI-generated style reviews for my chapters.
*   **Acceptance Criteria:**
    *   1: Tool `save_review(uuid, review_text)` stores style feedback.
    *   2: Tool `get_review(uuid)` retrieves stored reviews.
    *   3: Stored in `.ai-assistant/reviews/{uuid}.md`.
    *   4: Review includes: strengths, weaknesses, style suggestions.

#### Story 5.2: Batch Analysis Tool
*   As a User, I want to analyze a chapter once and get summary, metadata, and style review in one operation.
*   **Acceptance Criteria:**
    *   1: Tool `analyze_chapter(uuid, tasks)` performs multiple analyses.
    *   2: `tasks` parameter accepts array: `["summary", "metadata", "review"]`.
    *   3: Returns structured results for all requested tasks.
    *   4: Reads chapter content only once.
    *   5: Graceful partial success (if one task fails, others succeed).

#### Story 5.3: Review Archiving
*   As a User, I want previous reviews to be automatically archived when a new one is saved, so I can track progress.
*   **Acceptance Criteria:**
    *   1: `save_review` automatically moves existing review to `_archive/{uuid}/{timestamp}.md`.
    *   2: Current review file is always the latest one.
    *   3: Archived filenames use ISO timestamp.

#### Story 5.4: Review Comparison
*   As an AI, I want to fetch previous reviews to compare them with the current version.
*   **Acceptance Criteria:**
    *   1: Tool `get_review_history(uuid)` returns list of available past reviews.
    *   2: Tool `get_previous_review(uuid)` returns the content of the most recent archived review.
    *   3: Tool `get_archived_review(uuid, timestamp)` returns content of a specific archived version.

### Epic 6: World Building
**Goal:** Manage persistent data for Characters and Locations to ensure consistency across the project.

#### Story 6.1: Character & Location Storage
*   As a User, I want to store character and location profiles in dedicated folders, so the AI can reference them.
*   **Acceptance Criteria:**
    *   1: Configurable folders: `.ai-assistant/characters` and `.ai-assistant/locations`.
    *   2: One file per entity (e.g., `Gandalf.md`, `Rivendell.md`).
    *   3: Support for "hybrid" filenames if linked to binder (optional, but good for consistency).

#### Story 6.2: World Building Tools
*   As an AI, I want tools to creating/reading/listing characters and locations.
*   **Acceptance Criteria:**
    *   1: Tools: `save_character`, `get_character`, `list_characters`.
    *   2: Tools: `save_location`, `get_location`, `list_locations`.
    *   3: `list_*` tools should return names of available entities to help the AI know what to fetch.

