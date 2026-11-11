# Scrivener Assistant

A writing companion for authors using [Scrivener](https://www.literatureandlatte.com/scrivener/overview). It gives AI agents deep access to your `.scriv` project and provides a structured workflow for brainstorming, drafting, reviewing, and maintaining world continuity across chapters.

It can be installed as a **Desktop Extension (MCPB)** for one-click setup, run manually as a **Model Context Protocol (MCP)** server, or used as a standalone **Command Line Interface (CLI)**.

## [📖 User Guide](docs/user_guide.md) — Start Here

Read the **[User Guide](docs/user_guide.md)** to set up the writing workflow (brainstorm → draft → review → state tracking).

## Features

**Reading your project**
- Load any `.scriv` project (Scrivener 3 format)
- Navigate the manuscript binder (DraftFolder only — non-writing sections excluded)
- Read document text (auto-converted from RTF), inspector notes, and index card synopses
- Read and write custom metadata fields and the native Scrivener status

**Writing workflow (Claude Code agents)**
- `brainstorm-agent` — plan next chapters through dialogue, with continuity guardrails
- `draft-agent` — generate scene beats then prose, fill TODO markers in existing text
- `review-agent` — 5-point quality review, score, summary, metadata extraction, state update
- `scene-chronicler` — full enrichment pipeline for any existing scene (character sheets, location sheets, world file updates)

**Author voice** — drafts that sound like you, and get better as you retouch them
- `voice-bootstrap` prompt — one-time setup from chapters you wrote yourself: a measured baseline, a voice guide (characteristic moves, numeric targets, banned AI-isms) and exemplar passages. Available as an **MCP prompt**, so it works in Claude Desktop (prompts "+" menu) as well as in Claude Code.
- Deterministic French style metrics (`voice_stats`, `compare_voice_stats`): sentence and paragraph length, dialogue share, `on` and `-ment` adverb frequency, sentence-opening variety, tense mix.
- Hand-off (`handoff_draft`): freezes the AI draft as `draft.sent.md` (the diff baseline) before you retouch it. For legacy chapters that mix your text and AI text and were never frozen, `source="scrivener"` freezes the current Scrivener text instead; the later diff is then flagged `legacy-mixed` and counts as weak evidence only.
- Retouch measurement (`compute_rewrite_diff`): compares the AI draft with your retouched text in Scrivener and reports the edit rate and every before → after edit. `[AUTEUR: …]` placeholders you fill in are not counted as edits.
- Chapters are resolved by number or title from the scene registry (`resolve_chapter_scenes`).
- Learning loop (edit classification, rules promoted after several chapters, voice judge, predicted edits): planned — see [TODOS.md](TODOS.md) and the [design](docs/superpowers/specs/2026-11-10-author-voice-design.md).

**World & story data**
- `world/` — style guide, universe bible, structure, plan, timeline, relations (human-editable)
- `state/` — versioned per-chapter snapshots (situation, characters, knowledge, inventory)
- `drafts/` — brainstorm notes, scene beats, AI-generated prose per chapter
- `voice/` — voice guide, rule hypotheses, baseline metrics, exemplars, per-chapter edit diffs, progress ledger
- Character and location profile database
- Versioned review history (timestamped, browsable)
- `scene_registry.json` — aggregated per-scene metadata (word count, synopsis, status, summary, review flag), auto-updated on every write

**Safety**
- Read-only access to Scrivener content — your manuscript is never modified
- All AI data lives in `.ai-assistant/` inside the `.scriv` bundle

## Installation

### Option A: Desktop Extension (Recommended)
No Python installation required: the extension runs the server with [uv](https://github.com/astral-sh/uv), which installs Python and the dependencies automatically. uv itself must be installed first (`brew install uv` on macOS) — without it the extension does not start.

1. Download the latest `scrivener-assistant.mcpb` from the [Releases](https://github.com/elnino1/scrivener-assistant/releases) page.
2. Double-click the `.mcpb` file — Claude Desktop will install it.
3. Optionally set your project path in the extension settings UI.

To build the `.mcpb` file yourself (files listed in `.mcpbignore` are left out):
```bash
npx -y @anthropic-ai/mcpb pack . scrivener-assistant-dev.mcpb
```
A local build keeps the `0.0.0-dev` version: uninstall the previous extension in Claude Desktop before installing it.

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

48 tools are exposed. Key ones:

| Category | Tools |
|----------|-------|
| **Project** | `set_project_path`, `get_current_project`, `get_binder_structure` |
| **Reading** | `read_document`, `read_document_notes`, `read_document_synopsis`, `prepare_chapter_analysis` |
| **Metadata** | `update_metadata`, `list_native_statuses`, `update_native_status` |
| **Scene registry** | `rebuild_scene_registry`, `get_scene_registry` |
| **World** | `get_world`, `save_world` |
| **State** | `get_story_state`, `save_story_state`, `list_story_states` |
| **Drafts** | `save_brainstorm`, `save_beats`, `save_draft`, `get_draft` |
| **Reviews** | `save_review`, `get_review`, `get_review_history`, `get_previous_review`, `get_archived_review` |
| **Summaries** | `save_summary`, `get_summary` |
| **Characters** | `save_character`, `get_character`, `list_characters` |
| **Locations** | `save_location`, `get_location`, `list_locations` |
| **Prompts** | `save_prompt`, `get_prompt`, `list_prompts` |
| **Voice** | `resolve_chapter_scenes`, `voice_stats`, `compare_voice_stats`, `compute_voice_baseline`, `handoff_draft`, `compute_rewrite_diff`, `get_voice`, `save_voice`, `save_voice_exemplar`, `list_voice_exemplars`, `get_voice_exemplar` |
| **Extraction** | `extract_bible_from_chapters` |

MCP prompts: `voice-bootstrap` (optional `corpus` argument). See [docs/REFERENCE.md](docs/REFERENCE.md).

## Development

```bash
uv run --extra dev pytest
# or: pip install ".[dev]" && pytest
```

Roadmap: [TODOS.md](TODOS.md).
