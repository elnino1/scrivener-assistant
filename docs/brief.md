# Project Brief: Scrivener Assistant MCP

## Executive Summary
The **Scrivener Assistant MCP** is a Model Context Protocol server designed to bridge the gap between Scrivener's rich writing environment and Large Language Models. It enables AI agents to directly access, read, and analyze Scrivener projects (`.scriv`), allowing for high-level editorial feedback, consistency checking, and brainstorming support that understands the full context of a manuscript.

## Problem Statement
Scrivener is the gold standard for long-form writing, but getting AI assistance on a large, multi-document project is currently fragmented. Writers have to copy-paste individual scenes into generic chat interfaces, losing the broader context of the binder structure, character notes, and previous chapters. This leads to disjointed feedback that fails to account for the narrative arc or project-specific details.

## Proposed Solution
A specialized MCP server that parses the Scrivener package format. It provides tools for:
*   **Reading Context:** Fetching the Binder structure and content of specific documents/cards.
*   **Analysis:** Aggregating character sketches, locations, and notes alongside the manuscript text.
*   **Feedback:** Enabling the AI to provide improvements, plot hole detection, and stylistic advice based on the *entire* project state.

## Target Users
### Primary User Segment: Long-form Authors
*   **Profile:** Fiction & Non-Fiction Authors using Scrivener.
*   **Pain Points:** Struggle to keep track of all details across large projects; difficult to get high-level developmental editing feedback without expensive human editors.
*   **Goal:** Maintain narrative consistency and get "big picture" feedback.

### Secondary User Segment: Academics & Screenwriters
*   **Profile:** Researchers and screenwriters who rely on Scrivener's structural tools.
*   **Pain Points:** Need to synthesize information from many research notes or scenes.

## Goals & Success Metrics
### Business Objectives
*   Deliver a working MCP server that demonstrates the power of context-aware AI assistance for complex documents.

### User Success Metrics
*   AI can correctly identify the project structure (Binder).
*   AI can read specific scenes/chapters without manual user copy-pasting.
*   User receives relevant feedback (plot holes, consistency) based on the *actual* project content.

### Key Performance Indicators (KPIs)
*   **Connection Success Rate:** successful connection to a `.scriv` file.
*   **Retrieval Accuracy:** correct retrieval of text content from internal RTF files.

## MVP Scope
### Core Features (Must Have)
*   **Project Connection:** Ability to point the server to a local `.scriv` file path.
*   **Binder Parsing:** Tool `get_binder_structure` to return the hierarchy of folders and documents (titles, IDs).
*   **Content Extraction:** Tool `read_document(id)` to extract plain text from the internal RTF files of Scrivener.
*   **Metadata:** Ability to read basic metadata (synopsis, notes) associated with a document.

### Out of Scope for MVP
*   **Write Access:** Modifying or writing back to the Scrivener project files (risk of corruption).
*   **Creation:** Creating new documents or folders.
*   **GUI:** This will be a headless MCP server.

### MVP Success Criteria
The MVP is successful if an AI agent (like Claude) can read a user's Scrivener project binder, select a specific chapter, read its text, and summarize it back to the user accurately.

## Post-MVP Vision
*   **Phase 2:** Two-way synchronization (accepting AI edits safely), sophisticated search across the project.
*   **Long-term:** Generative features (creating scenes from prompts), deep integration with Scrivener's "Research" folder, acting as a co-writer.

## Technical Considerations
### Platform Requirements
*   **Target:** Local Execution (MCP Server).
*   **OS:** Cross-platform (Mac/Windows) where Scrivener runs, but initially focused on Mac (user environment).

### Technology Preferences
*   **Language:** Python (Strong ecosystem for text processing and file handling).
*   **Parsing:** `pyrtf-ng` or similar for RTF parsing; `xml.etree` for parsing `.scrivx` binder structure.

### Constraints & Assumptions
*   **Constraint:** Local execution only for privacy.
*   **Risk:** The `.scriv` format is proprietary (though largely XML + RTF). Parsing RTF correctly to plain text without losing meaning is the main technical challenge.
*   **Assumption:** Users have a valid Scrivener 3 project format.

## Next Steps
1.  **PM Handoff:** Proceed to PRD creation using this brief as the foundational truth.
