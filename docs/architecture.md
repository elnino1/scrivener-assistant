# Scrivener Assistant MCP Architecture Document

## Introduction
This document outlines the architectural blueprint for the Scrivener Assistant MCP. It details the system structure, technology choices, and component design to ensure a robust, maintainable, and context-aware integration between Scrivener and AI agents.

### Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2026-01-21 | 1.0 | Initial Architecture | Architect Agent |

## High Level Architecture
### Technical Summary
The system is designed as a **Monolithic Python Package** that functions as a local Model Context Protocol (MCP) server. It uses a succinct **Service Layer Pattern** to separate the MCP interface (Presentation) from the core Scrivener parsing logic (Business Logic). The system interacts directly with the local file system to read proprietary Scrivener formats (`.scrivx` XML and `.rtf` content), converting them into clean text for AI consumption.

### High Level Overview
*   **Style:** Local Monolithic Server.
*   **Repository:** Single Repository.
*   **Flow:** `MCP Client (Claude)` -> `stdio (JSON-RPC)` -> `MCP Server` -> `ScrivenerService` -> `Local File System`.

### Architecture Diagram
```mermaid
graph TD
    Client[AI Agent / Client] -- "JSON-RPC (stdio)" --> Server[server.py (MCP Entry Point)]
    subgraph "Scrivener Assistant MCP"
        Server -- "Calls" --> Service[ScrivenerService]
        Service -- "Parses Binder" --> BinderParser[binder_parser.py]
        Service -- "Extracts Text" --> ContentParser[content_parser.py]
    end
    subgraph "File System"
        BinderParser -- "Reads .scrivx" --> ScrivFile[.scriv Folder]
        ContentParser -- "Reads .rtf" --> RTFFiles[Files/Data/*.rtf]
    end
```

## Tech Stack
| Category | Technology | Version | Purpose | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Language** | Python | 3.10+ | Primary Language | Excellent for text processing and file manipulation. |
| **MCP SDK** | `mcp` | Latest | MCP Implementation | Official SDK for building MCP servers. |
| **Parsing** | `xml.etree` | Native | XML Parsing | Robust, built-in library for parsing `.scrivx` files. |
| **Parsing** | `striprtf` | Latest | RTF Conversion | Lightweight library to convert RTF to plain text. |
| **Testing** | `pytest` | Latest | Testing Framework | Standard for Python ecosystem. |

## Data Models
### BinderNode
Represents a single item in the Scrivener Binder (Folder, Text, Trash).
*   **Attributes:**
    *   `uuid` (str): Unique identifier from `.scrivx`.
    *   `title` (str): Display title of the node.
    *   `type` (str): Type of node (e.g., "Folder", "Text").
    *   `children` (List[BinderNode]): Nested items.

### ScrivenerProject
Represents the loaded project state.
*   **Attributes:**
    *   `path` (str): Absolute path to the `.scriv` directory.
    *   `root` (BinderNode): Root of the binder tree.
*   **Responsibilities:**
    *   Loading and validating the project path.
    *   Providing access to the binder interaction logic.

## Components
### 1. Server Entry Point (`server.py`)
*   **Responsibility:** Initializes the MCP server, registers tools, and handles the main event loop.
*   **Tools:**
    *   `set_project_path(path)`: Dynamically load a project.
    *   `get_binder_structure()`: Returns the binder tree JSON.
    *   `read_document(uuid)`: Returns text content for a document.

### 2. Scrivener Reader Package (`scrivener_reader/`)
*   **`__init__.py`**: Expoerts the main `ScrivenerProject` class.
*   **`binder_parser.py`**: Contains `parse_scrivx(path) -> BinderNode`. Handles recursion and XML parsing.
*   **`content_parser.py`**: Contains `read_content(project_path, uuid) -> str`. Maps UUID to file path `Files/Data/{n}.rtf` (requiring lookup in `.scrivx` or mapping logic) and runs RTF stripping.
*   **`utils.py`**: General file system helpers.

## Source Tree
```text
scrivener-assistant-mcp/
├── src/
│   ├── server.py               # Main entry point
│   └── scrivener_reader/       # Core Logic Package
│       ├── __init__.py
│       ├── binder_parser.py
│       ├── content_parser.py
│       └── utils.py
├── tests/
│   ├── fixtures/               # Sample .scriv projects
│   ├── test_binder_parser.py
│   └── test_content_parser.py
├── pyproject.toml              # Dependencies
└── README.md
```

## Security & input Validation
*   **Path Traversal:** Validate that any provided project path is a valid directory and (optional but recommended) ideally strictly within user-approved zones if applicable.
*   **File Existence:** Gracefully handle missing RTF files (e.g., empty documents) without crashing.
*   **Data Only:** Read-only access ensures no corruption of the user's precious manuscript.

## Next Steps
1.  **Handoff:** Architecture is complete.
2.  **Implementation:** Switch to Dev Agent (`/dev`) to begin **Epic 1: Foundation & Binder Navigation**.
