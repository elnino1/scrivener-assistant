# Scrivener Assistant

A writing companion for authors using [Scrivener](https://www.literatureandlatte.com/scrivener/overview). It gives AI agents deep access to your `.scriv` project and provides a structured workflow for brainstorming, drafting, reviewing, and maintaining world continuity across chapters.

It can be installed as a **Desktop Extension (MCPB)** for one-click setup, run manually as a **Model Context Protocol (MCP)** server, or used as a standalone **Command Line Interface (CLI)**.

## [📖 User Guide](docs/user_guide.md) — Start Here

Read the **[User Guide](docs/user_guide.md)** to set up the writing workflow (brainstorm → draft → review → state tracking).

## Features

**Reading your project**
- Load any `.scriv` project (Scrivener 3 format)
- Navigate the full binder hierarchy
- Read document text (auto-converted from RTF), inspector notes, and index card synopses
- Read and write custom metadata fields

**Writing workflow (Claude Code agents)**
- `brainstorm-agent` — plan next chapters through dialogue, with continuity guardrails
- `draft-agent` — generate scene beats then prose, fill TODO markers in existing text
- `review-agent` — 5-point quality review, score, summary, metadata extraction, state update
- `scene-chronicler` — full enrichment pipeline for any existing scene (character sheets, location sheets, world file updates)

**World & story data**
- `world/` — style guide, universe bible, structure, plan, timeline, relations (human-editable)
- `state/` — versioned per-chapter snapshots (situation, characters, knowledge, inventory)
- `drafts/` — brainstorm notes, scene beats, AI-generated prose per chapter
- Character and location profile database
- Versioned review history (timestamped, browsable)

**Safety**
- Read-only access to Scrivener content — your manuscript is never modified
- All AI data lives in `.ai-assistant/` inside the `.scriv` bundle

## Installation

### Option A: Desktop Extension (Recommended)
No Python installation required. Claude Desktop uses [UV](https://github.com/astral-sh/uv) to manage the Python environment automatically.

1. Download the latest `scrivener-assistant.mcpb` from the [Releases](https://github.com/elnino1/scrivener-assistant/releases) page.
2. Double-click the `.mcpb` file — Claude Desktop will install it.
3. Optionally set your project path in the extension settings UI.

To build the `.mcpb` file yourself:
```bash
npm install -g @anthropic-ai/mcpb
mcpb pack .
```

### Option B: Manual Installation (Advanced)

#### Prerequisites
- Python 3.10 or higher
- `uv` (recommended) or `pip`

```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the latest version directly from GitHub
pip install git+https://github.com/elnino1/scrivener-assistant.git
```

#### Installing from Source (For Developers)
```bash
git clone https://github.com/elnino1/scrivener-assistant.git
cd scrivener-assistant
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

This project can be used in three ways: as a **Desktop Extension (MCPB)**, as a manual **MCP Server**, or as a standalone **CLI**.

---

### Option 1: Desktop Extension (MCPB) — Recommended

Install the `.mcpb` file as described above. Once installed, Claude Desktop launches the server automatically. You can optionally configure your Scrivener project path in the extension settings UI — or leave it blank and use the `set_project_path` tool at any time.

---

### Option 2: MCP Server (Manual)

```bash
# Run with default settings (no project loaded)
python src/server.py

# Load a default project on startup
python src/server.py -p /path/to/my/project.scriv

# Enable verbose debug logging
python src/server.py -p /path/to/my/project.scriv -v
```

**Available options:**
- `-p, --project PATH` — path to the .scriv project directory
- `-s, --storage PATH` — override the `.ai-assistant/` folder location
- `-v, --verbose` — enable debug logging
- `-h, --help` — show help

**Configuration (Claude Desktop):**
```json
{
  "mcpServers": {
    "scrivener": {
      "command": "python3",
      "args": [
        "/absolute/path/to/scrivener-assistant-mcp/src/server.py",
        "-p", "/optional/path/to/project.scriv"
      ]
    }
  }
}
```

---

### Option 3: CLI

```bash
# Get binder structure
scrivener-cli -p /path/to/project.scriv binder

# Read a document
scrivener-cli -p /path/to/project.scriv read <uuid>

# List characters
scrivener-cli -p /path/to/project.scriv character list
```

Run `scrivener-cli --help` for a full list of commands.

---

## MCP Tools Reference

34 tools are exposed. Key ones:

| Category | Tools |
|----------|-------|
| **Project** | `set_project_path`, `get_current_project`, `get_binder_structure` |
| **Reading** | `read_document`, `read_document_notes`, `read_document_synopsis`, `prepare_chapter_analysis` |
| **Metadata** | `update_metadata` |
| **World** | `get_world`, `save_world` |
| **State** | `get_story_state`, `save_story_state`, `list_story_states` |
| **Drafts** | `save_brainstorm`, `save_beats`, `save_draft`, `get_draft` |
| **Reviews** | `save_review`, `get_review`, `get_review_history`, `get_previous_review`, `get_archived_review` |
| **Summaries** | `save_summary`, `get_summary` |
| **Characters** | `save_character`, `get_character`, `list_characters` |
| **Locations** | `save_location`, `get_location`, `list_locations` |
| **Prompts** | `save_prompt`, `get_prompt`, `list_prompts` |
| **Extraction** | `extract_bible_from_chapters` |

## Development

```bash
pip install ".[dev]"
pytest
```
