# Implementation Plan — Writing Workflow

**Spec:** [2026-04-20-writing-workflow-design.md](./2026-04-20-writing-workflow-design.md)
**Branch:** `feat/add_agents`

---

## Overview

This plan implements the writing workflow in 4 phases:

1. **Config + Migration** — update paths, move characters/locations into `world/`
2. **New managers** — `WorldManager`, `StateManager`, `DraftManager`
3. **New MCP tools** — 10 new tools wired through `ScrivenerProject`
4. **Agent definitions** — 3 agents in `.claude/agents/`

Each phase is independently testable. Complete and verify each before starting the next.

---

## Phase 1 — Config & Migration

### Step 1.1 — Update `config.py`

File: `src/scrivener_assistant/config.py`

Add new subfolders and update character/location paths:

```python
@dataclass
class ProjectConfig:
    assistant_folder: str = field(default_factory=lambda: os.getenv("SCRIVENER_ASSISTANT_FOLDER", ".ai-assistant"))
    prompts_subfolder: str = "prompts"
    summaries_subfolder: str = "summaries"
    reviews_subfolder: str = "reviews"
    # moved into world/
    characters_subfolder: str = "world/characters"
    locations_subfolder: str = "world/locations"
    # new
    world_subfolder: str = "world"
    state_subfolder: str = "state"
    drafts_subfolder: str = "drafts"
    max_backups: int = 5
```

### Step 1.2 — Add migration tool for characters/locations

File: `src/scrivener_assistant/migration_tool.py` (already exists — extend it)

Add a `migrate_characters_locations(project_path, config)` function that:
- Checks if `.ai-assistant/characters/` exists
- Moves it to `.ai-assistant/world/characters/` if present
- Checks if `.ai-assistant/locations/` exists
- Moves it to `.ai-assistant/world/locations/` if present
- Logs each moved file
- Is idempotent (safe to run twice)

### Step 1.3 — Run migration on project load

File: `src/scrivener_assistant/project.py`

In `ScrivenerProject.__init__`, after managers are initialized, call `migrate_characters_locations`. This ensures the migration happens automatically when the project is loaded, without requiring a manual step.

**Verification:** Load the real Scrivener project, confirm characters and locations are accessible at new paths and old paths no longer exist.

---

## Phase 2 — New Managers

### Step 2.1 — `WorldManager`

New file: `src/scrivener_assistant/world_manager.py`

Manages `world/` flat files. Unlike `BaseSceneDataManager` (which manages UUID-keyed scene data), this manages named top-level files.

```python
class WorldManager:
    VALID_SECTIONS = {"style", "bible", "structure", "plan", "timeline", "synthesis"}

    def __init__(self, project_path: Path, config: ProjectConfig): ...

    def get_section(self, section: str) -> Optional[str]:
        """Read world/<section>.md. Returns None if not found."""

    def get_all(self) -> dict[str, str]:
        """Read all world/ files. Returns {section: content}."""

    def save_section(self, section: str, content: str) -> Path:
        """Write world/<section>.md. Raises ValueError for unknown sections."""

    def list_sections(self) -> list[str]:
        """List all .md files present in world/."""
```

`world/` path = `project_path / config.assistant_folder / config.world_subfolder`

### Step 2.2 — `StateManager`

New file: `src/scrivener_assistant/state_manager.py`

Manages `state/current/` (4 files) and archived `state/chapter-NN/` snapshots.

```python
class StateManager:
    STATE_FILES = ["situation", "characters", "knowledge", "inventory"]

    def __init__(self, project_path: Path, config: ProjectConfig): ...

    def get_current(self) -> Optional[dict[str, str]]:
        """Read all 4 files from state/current/. Returns {name: content} or None if not initialized."""

    def get_chapter(self, chapter: int) -> Optional[dict[str, str]]:
        """Read state/chapter-NN/ snapshot."""

    def save_state(self, chapter: int, situation: str, characters: str, knowledge: str, inventory: str) -> Path:
        """
        Archive current state to state/chapter-NN/, then write new state to state/current/.
        chapter_folder format: chapter-05 (zero-padded to 2 digits).
        """

    def list_snapshots(self) -> list[str]:
        """Return sorted list of archived chapter folder names."""
```

`state/` path = `project_path / config.assistant_folder / config.state_subfolder`

### Step 2.3 — `DraftManager`

New file: `src/scrivener_assistant/draft_manager.py`

Manages `drafts/chapter-NN/` working files.

```python
class DraftManager:
    DRAFT_FILES = ["brainstorm", "beats", "draft"]

    def __init__(self, project_path: Path, config: ProjectConfig): ...

    def save_file(self, chapter: int, file_type: str, content: str) -> Path:
        """Write drafts/chapter-NN/<file_type>.md. Validates file_type."""

    def get_file(self, chapter: int, file_type: str) -> Optional[str]:
        """Read drafts/chapter-NN/<file_type>.md."""

    def list_chapters(self) -> list[str]:
        """Return sorted list of chapter folder names that have at least one draft file."""
```

`drafts/` path = `project_path / config.assistant_folder / config.drafts_subfolder`

### Step 2.4 — Wire into `ScrivenerProject`

File: `src/scrivener_assistant/project.py`

Add to `__init__`:
```python
from scrivener_assistant.world_manager import WorldManager
from scrivener_assistant.state_manager import StateManager
from scrivener_assistant.draft_manager import DraftManager

self.world_manager = WorldManager(self.path, self.config)
self.state_manager = StateManager(self.path, self.config)
self.draft_manager = DraftManager(self.path, self.config)
```

Add thin proxy methods on `ScrivenerProject` for each manager operation (consistent with existing pattern where `project.save_summary()` delegates to `summary_manager`).

**Verification:** Write a small test script that loads the project and calls `world_manager.get_all()`, `state_manager.get_current()`, `draft_manager.list_chapters()` without errors.

---

## Phase 3 — New MCP Tools

File: `src/server.py`

Add 10 new `@mcp.tool()` functions. Follow the existing pattern: guard with `if not current_project`, delegate to `current_project.*`, return string.

### World tools (2)

```python
@mcp.tool()
def get_world(section: str = "") -> str:
    """
    Reads world context files from world/.
    Args:
        section: One of style, bible, structure, plan, timeline, synthesis.
                 Leave empty to get all sections concatenated.
    """

@mcp.tool()
def save_world(section: str, content: str) -> str:
    """
    Writes a world context file.
    Args:
        section: One of style, bible, structure, plan, timeline, synthesis.
        content: Full markdown content to write.
    """
```

### State tools (3)

```python
@mcp.tool()
def get_story_state(chapter: int = 0) -> str:
    """
    Reads story state.
    Args:
        chapter: Chapter number to read archived state for.
                 Pass 0 (default) to read current state.
    Returns JSON with keys: situation, characters, knowledge, inventory.
    """

@mcp.tool()
def save_story_state(chapter: int, situation: str, characters: str, knowledge: str, inventory: str) -> str:
    """
    Saves a chapter state snapshot and updates state/current/.
    Archives the previous current state first.
    Args:
        chapter: The chapter number just completed.
        situation, characters, knowledge, inventory: Content for each state file.
    """

@mcp.tool()
def list_story_states() -> str:
    """Lists all archived chapter state snapshots."""
```

### Draft tools (4)

```python
@mcp.tool()
def save_brainstorm(chapter: int, content: str) -> str:
    """Saves brainstorm notes for a chapter to drafts/chapter-NN/brainstorm.md."""

@mcp.tool()
def save_beats(chapter: int, content: str) -> str:
    """Saves scene beats for a chapter to drafts/chapter-NN/beats.md."""

@mcp.tool()
def save_draft(chapter: int, content: str) -> str:
    """Saves AI-generated prose for a chapter to drafts/chapter-NN/draft.md."""

@mcp.tool()
def get_draft(chapter: int) -> str:
    """Reads the AI draft for a chapter from drafts/chapter-NN/draft.md."""
```

### Extraction tool (1)

```python
@mcp.tool()
def extract_bible_from_chapters(uuids: list[str]) -> str:
    """
    Reads a list of Scrivener documents and returns a structured analysis
    suitable for populating world/ files.

    The analysis covers:
    - Style patterns (POV, tense, tone, vocabulary)
    - Characters (names, traits, relationships detected in text)
    - Locations (settings detected in text)
    - Narrative arc (themes, turning points)

    Does NOT save anything — returns the analysis as text for user review.
    The user then calls save_world() and save_character() to persist what they want.

    Args:
        uuids: List of document UUIDs to analyze.
    """
```

Implementation: reads each UUID via `current_project.read_document()`, concatenates content, returns a structured prompt-response asking Claude to analyze and format the output. Does not call an LLM itself — returns the aggregated text with analysis instructions embedded, so Claude (the caller) performs the analysis.

**Verification:** Start the MCP server, confirm all 10 new tools appear in the tool list without errors.

---

## Phase 4 — Agent Definitions

Create `.claude/agents/` in the project root (not inside `src/`).

### `brainstorm-agent.md`

```markdown
---
name: brainstorm-agent
description: Interactive story planning agent. Use when the user wants to plan the next chapter(s). Loads full world context and current state, then engages in dialogue to explore plot directions, continuity risks, and character arcs.
model: claude-sonnet-4-6
---

You are a story planning assistant for the novel "Mère".

On start:
1. Call `get_world()` to load full world context (style, bible, structure, plan, timeline, synthesis)
2. Call `get_story_state()` to load current story state
3. Call `get_summary` on the last 2 chapters (ask the user for their UUIDs if unknown)

Then:
- Ask the user what they have in mind for the next chapter(s)
- Raise continuity risks based on state/current/knowledge.md (what each character knows)
- Surface open story hooks from state/current/situation.md
- Suggest 2-3 plot directions when the user is open to ideas
- Keep the dialogue focused — one question or observation per turn
- When the user is satisfied with the direction, summarize the decisions and ask to save

To save: call `save_brainstorm(<chapter_number>, <summary_of_decisions>)`
Ask the user for the chapter number if not clear.
```

### `draft-agent.md`

```markdown
---
name: draft-agent
description: Chapter drafting agent. Use after brainstorm is complete. Reads brainstorm notes, world context and current state, then writes scene beats followed by prose. Saves both to drafts/.
model: claude-opus-4-7
---

You are a chapter writer for the novel "Mère".

On start:
1. Ask the user for the chapter number to draft
2. Call `get_world()` — load full world context
3. Call `get_story_state()` — load current state
4. Call `get_draft(<chapter>)` on brainstorm.md — if missing, warn and ask to run brainstorm-agent first

Phase 1 — Beats:
- Write 5–8 scene beats that advance the story per brainstorm direction
- Each beat: one sentence describing what happens, which character is focal, and the emotional note
- Beats must respect: style guide (POV, tense), continuity (state files), open hooks
- Call `save_beats(<chapter>, <beats>)` and show the beats to the user
- Ask: "Should I proceed to writing the prose, or do you want to adjust the beats?"

Phase 2 — Prose:
- Write the full chapter draft following the approved beats
- Respect style.md exactly: 3rd person limited, past tense, rhythm patterns, vocabulary register
- Save with `save_draft(<chapter>, <prose>)`
- Remind the user: "The draft is saved to drafts/chapter-NN/draft.md. Copy it into Scrivener and rewrite as you see fit. Then run review-agent with the Scrivener UUID."
```

### `review-agent.md`

```markdown
---
name: review-agent
description: Chapter review agent. Use after the human has rewritten a chapter in Scrivener. Reads the Scrivener document by UUID, runs style/character/continuity checks, saves a review, and updates story state.
model: claude-sonnet-4-6
---

You are a chapter reviewer for the novel "Mère".

On start:
1. Ask the user for the Scrivener UUID of the chapter they want reviewed
2. Ask for the chapter number (for state archiving)
3. Call `get_world()` — load full world context
4. Call `get_story_state()` — load current state
5. Call `read_document(<uuid>)` — read the chapter

Run three sequential checks, reporting each one:

**Check 1 — Style**
Compare against world/style.md:
- POV consistency (3rd person limited, no omniscient slips)
- Tense correctness (past tense, imparfait/passé simple distinction)
- Rhythm patterns (short/long sentence alternation)
- Vocabulary register (no anachronisms, period-appropriate)
- Report: issues found with quoted examples, or PASS

**Check 2 — Character authenticity**
Compare against world/characters/ and state/current/characters.md:
- Each character's dialogue and reactions match their established personality
- Emotional continuity from previous chapter
- No knowledge violations (character acts on information they don't have)
- Report: issues found with quoted examples, or PASS

**Check 3 — Continuity**
Compare against state/current/:
- Physical positions of characters match situation.md
- Timeline is consistent with timeline.md
- Objects referenced exist and are in the right place per inventory.md
- Report: issues found, or PASS

After all checks:
- Call `save_review(<uuid>, <full_review_text>)`
- Call `save_story_state(<chapter>, <situation>, <characters>, <knowledge>, <inventory>)` with updated state extracted from the chapter
- If new characters or locations appeared, prompt: "I noticed [X] — should I save a profile? Call save_character() or save_location() if yes."
- Remind the user: "State updated for chapter <N>. The next brainstorm session will pick this up automatically."
```

**Verification:** Open Claude Code, confirm all 3 agents are discoverable. Run a quick test: trigger `brainstorm-agent`, confirm it calls `get_world()` and `get_story_state()` on start.

---

## Execution Order

```
Phase 1: Step 1.1 → 1.2 → 1.3 → verify
Phase 2: Step 2.1 → 2.2 → 2.3 → 2.4 → verify
Phase 3: all 10 tools → verify server starts cleanly
Phase 4: 3 agent files → verify in Claude Code
```

Phases 2 and 3 can be parallelized (managers and tools are independent until step 2.4 wires them together). Phase 4 has no code dependencies — it can be written at any time.

---

## Files Changed / Created

| File | Action |
|------|--------|
| `src/scrivener_assistant/config.py` | Edit — new subfolders, updated character/location paths |
| `src/scrivener_assistant/migration_tool.py` | Edit — add `migrate_characters_locations()` |
| `src/scrivener_assistant/project.py` | Edit — add 3 new managers + auto-migration on load |
| `src/scrivener_assistant/world_manager.py` | New |
| `src/scrivener_assistant/state_manager.py` | New |
| `src/scrivener_assistant/draft_manager.py` | New |
| `src/server.py` | Edit — 10 new MCP tools |
| `.claude/agents/brainstorm-agent.md` | New |
| `.claude/agents/draft-agent.md` | New |
| `.claude/agents/review-agent.md` | New |
