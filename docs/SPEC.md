# Scrivener Assistant MCP — Specification

> **Living document.** This spec reflects what is currently implemented.
> For the writing workflow and agent usage guide, see `user_guide.md`.

---

## 1. Objective

A local **Model Context Protocol (MCP) server** that bridges Scrivener and AI agents. It gives AI agents direct, structured access to a Scrivener project — reading content, writing analysis results back to the project, and maintaining a persistent knowledge base that spans the full manuscript.

**Target users:** Fiction authors using Scrivener 3 who want AI assistance (developmental editing, consistency checking, brainstorming) that understands the full context of their project, not just isolated copy-pasted passages.

**Core constraint:** Local execution only. No data is sent to external services. The manuscript files are read-only; write operations target only the `.ai-assistant/` folder and the custom metadata section of the `.scrivx` file.

---

## 2. System Architecture

### Overview

```
MCP Client (Claude) ──JSON-RPC (stdio)──► server.py ──► ScrivenerProject
                                                               │
                          ┌────────────────────────────────────┤
                          │                                    │
                   .scriv/ (read)                    .ai-assistant/ (read/write)
                   ├── project.scrivx                ├── summaries/
                   └── Files/Data/{UUID}/            ├── reviews/
                       ├── content.rtf               ├── world/
                       ├── notes.rtf                 ├── state/
                       └── synopsis.txt              ├── drafts/
                                                     ├── prompts/
                                                     └── scene_registry.json
```

### Design decisions

- **Monolithic Python package** — a single `scrivener_assistant` package with a manager-per-concern pattern. No microservices.
- **Service façade** — `ScrivenerProject` is the single public API. `server.py` calls only `ScrivenerProject` methods; it never touches individual managers directly (except `review_manager` for history queries).
- **Manager pattern** — each concern lives in its own manager class. All managers extend `BaseSceneDataManager` (for scene-scoped data) or stand alone.
- **Dependency injection** — `ProjectConfig` is injected into all managers; `binder_map` is injected into scene managers at construction time. No hardcoded paths inside managers.
- **Atomic writes** — all JSON outputs and temporary files use `os.replace()` after writing to a `.tmp` file, preventing partial writes.

---

## 3. Tech Stack

| Category | Technology | Version | Purpose |
|---|---|---|---|
| Language | Python | 3.10+ | Primary language |
| MCP SDK | `mcp` (FastMCP) | Latest | MCP server implementation |
| XML parsing | `xml.etree.ElementTree` | stdlib | `.scrivx` binder parsing |
| RTF conversion | `striprtf` | Latest | RTF → plain text |
| Testing | `pytest` | Latest | Test runner |
| Packaging | `pyproject.toml` | — | Dependency management |

---

## 4. Source Tree

```
scrivener-assistant/
├── src/
│   ├── server.py                        # MCP entry point — 36 registered tools
│   └── scrivener_assistant/
│       ├── __init__.py                  # exports ScrivenerProject
│       ├── project.py                   # ScrivenerProject — main façade
│       ├── config.py                    # ProjectConfig dataclass
│       ├── base_manager.py              # BaseSceneDataManager — shared file I/O for scene data
│       ├── binder_parser.py             # BinderNode, parse_scrivx(), get_binder_map()
│       ├── content_parser.py            # get_content_path(), get_notes_path(), get_synopsis_path()
│       ├── rtf_converter.py             # convert_rtf_to_text()
│       ├── path_utils.py                # generate_hybrid_filename(), slugify(), get_short_uuid()
│       ├── metadata_manager.py          # MetadataManager — .scrivx custom metadata r/w
│       ├── summary_manager.py           # SummaryManager
│       ├── review_manager.py            # ReviewManager — with timestamped archiving
│       ├── prompt_manager.py            # PromptManager
│       ├── world_manager.py             # WorldManager — world/*.md sections
│       ├── state_manager.py             # StateManager — per-chapter state snapshots
│       ├── draft_manager.py             # DraftManager — brainstorm/beats/draft files
│       ├── scene_registry_manager.py    # SceneRegistryManager — scene_registry.json
│       └── migration_tool.py            # one-time migration helpers
│
├── tests/
│   ├── fixtures/
│   │   └── sample.scriv/               # sample Scrivener 3 project (test fixture)
│   ├── test_binder_parser.py
│   ├── test_content_parser.py
│   ├── test_rtf_converter.py
│   ├── test_metadata_manager.py
│   ├── test_scene_registry_manager.py
│   ├── test_lore.py
│   ├── test_project_validation.py
│   ├── test_review_versioning.py
│   ├── test_config_injection.py
│   ├── test_batch_analysis.py
│   ├── test_server.py
│   ├── test_integration_binder.py
│   ├── test_integration_content.py
│   ├── test_integration_metadata.py
│   ├── test_integration_reviews.py
│   ├── test_integration_summaries.py
│   ├── test_integration_prompts.py
│   └── test_integration_scene_registry.py
│
├── .claude/
│   └── agents/                         # Claude Code sub-agent definitions
│       ├── brainstorm-agent.md
│       ├── draft-agent.md
│       ├── review-agent.md
│       └── scene-chronicler.md
│
├── docs/
│   ├── SPEC.md                          # this document
│   └── user_guide.md                   # workflow guide for authors
│
├── pyproject.toml
└── README.md
```

---

## 5. Data Models

### `BinderNode`

Represents one item in the Scrivener binder.

```python
@dataclass
class BinderNode:
    uuid: str
    title: str
    type: str          # "Text", "Folder", "DraftFolder", "ResearchFolder", "TrashFolder", ...
    children: List["BinderNode"]
    parent: Optional["BinderNode"]

    def get_path(self) -> List[str]: ...   # ["Manuscript", "Chapter 1", "Scene"]
    def to_dict(self) -> dict: ...
```

### `ProjectConfig`

All configurable paths. Injected into every manager.

```python
@dataclass
class ProjectConfig:
    assistant_folder: str = ".ai-assistant"       # override via SCRIVENER_ASSISTANT_FOLDER
    prompts_subfolder: str = "prompts"
    summaries_subfolder: str = "summaries"
    reviews_subfolder: str = "reviews"
    characters_subfolder: str = "world/characters"
    locations_subfolder: str = "world/locations"
    world_subfolder: str = "world"
    state_subfolder: str = "state"
    drafts_subfolder: str = "drafts"
    scene_registry_filename: str = "scene_registry.json"
    max_backups: int = 5
```

### `ScrivenerProject`

Main façade. All MCP tools go through this object.

```python
class ScrivenerProject:
    path: Path
    config: ProjectConfig
    nodes: List[BinderNode]            # top-level binder nodes
    binder_map: dict[str, BinderNode]  # uuid → node (flat, all nodes)

    # Managers (one per concern)
    metadata_manager: MetadataManager
    prompt_manager: PromptManager
    summary_manager: SummaryManager
    review_manager: ReviewManager
    character_manager: BaseSceneDataManager
    location_manager: BaseSceneDataManager
    world_manager: WorldManager
    state_manager: StateManager
    draft_manager: DraftManager
    scene_registry: SceneRegistryManager
```

### `SceneRegistry` — per-scene JSON shape

```json
{
  "project": "MyNovel",
  "generated_at": "2026-05-06T14:30:00",
  "scene_count": 42,
  "scenes": [
    {
      "uuid": "21506607-96CA-4FB1-8B5F-A1859F4DCEDE",
      "title": "The Confrontation",
      "type": "Text",
      "binder_path": ["Manuscript", "Chapter 3", "The Confrontation"],
      "word_count": 1847,
      "synopsis": "Alice confronts Bob in the library.",
      "custom_metadata": { "Status": "Draft", "POV": "Alice" },
      "summary": "Full AI-generated summary text...",
      "has_review": true,
      "review_updated_at": "2026-05-06T12:00:00"
    }
  ]
}
```

Only `Text`-type nodes are included. Folder, Research, Trash nodes are excluded.

---

## 6. Storage Layout

Everything lives inside `.ai-assistant/` inside the `.scriv` bundle. The path can be overridden with the `SCRIVENER_ASSISTANT_FOLDER` environment variable or the `-s` CLI flag.

```
MyNovel.scriv/
└── .ai-assistant/
    ├── scene_registry.json          ← aggregated scene metadata (auto-maintained)
    ├── prompts/
    │   └── analyze_chapter.md
    ├── summaries/                   ← hierarchical: mirrors binder structure
    │   └── manuscript/chapter-1/scene-title--<short-uuid>.md
    ├── reviews/                     ← same hierarchy + timestamped archive
    │   ├── manuscript/chapter-1/scene-title--<short-uuid>.md
    │   └── _archive/<uuid>/<ISO-timestamp>.md
    ├── world/
    │   ├── synthesis.md             ← quick-reference context (loaded at session start)
    │   ├── bible.md                 ← universe rules and facts
    │   ├── style.md                 ← POV, tense, rhythm, vocabulary
    │   ├── structure.md             ← narrative arc and themes
    │   ├── plan.md                  ← chapter outline ([ÉCRIT]/[PRÉVU]/[ENVISAGÉ])
    │   ├── timeline.md              ← chronological event log
    │   ├── relations.md             ← character relationship map
    │   ├── characters/
    │   │   └── <name>.md
    │   └── locations/
    │       └── <name>.md
    ├── state/
    │   ├── current/
    │   │   ├── situation.md
    │   │   ├── characters.md
    │   │   ├── knowledge.md
    │   │   └── inventory.md
    │   └── chapter-05/              ← archived snapshot per completed chapter
    └── drafts/
        └── chapter-06/
            ├── brainstorm.md
            ├── beats.md
            └── draft.md
```

### File naming for summaries and reviews

Files use a hybrid name: `<slugified-title>--<short-uuid>.md`. This makes files human-readable while remaining UUID-addressable. If the binder structure is unknown, fallback is `<uuid>.md`.

---

## 7. MCP Tools Reference

### Project

| Tool | Signature | Description |
|---|---|---|
| `set_project_path` | `(path: str)` | Load a `.scriv` project |
| `get_current_project` | `()` | Return the active project path |
| `get_binder_structure` | `()` | Return the full binder tree as JSON |

### Content (read-only)

| Tool | Signature | Description |
|---|---|---|
| `read_document` | `(uuid: str)` | Plain text content of a scene |
| `read_document_notes` | `(uuid: str)` | Inspector notes (plain text) |
| `read_document_synopsis` | `(uuid: str)` | Scrivener synopsis (plain text) |

### Metadata

| Tool | Signature | Description |
|---|---|---|
| `update_metadata` | `(uuid, field, value)` | Write a custom metadata field to `.scrivx`. Creates the field definition if absent. Also triggers scene registry rebuild. |

### Summaries

| Tool | Signature | Description |
|---|---|---|
| `save_summary` | `(uuid, content)` | Save an AI-generated summary. Triggers registry rebuild. |
| `get_summary` | `(uuid)` | Retrieve a summary |

### Reviews

| Tool | Signature | Description |
|---|---|---|
| `save_review` | `(uuid, content)` | Save a style review. Archives previous if present. Triggers registry rebuild. |
| `get_review` | `(uuid)` | Retrieve current review |
| `get_review_history` | `(uuid)` | List all archived reviews (JSON array) |
| `get_previous_review` | `(uuid)` | Content of the most recent archived review |
| `get_archived_review` | `(uuid, timestamp)` | Content of a specific archived review |

### Analysis helpers

| Tool | Signature | Description |
|---|---|---|
| `prepare_chapter_analysis` | `(uuid)` | Read a chapter once and return it with a structured workflow prompt for summary + metadata + review |
| `extract_bible_from_chapters` | `(uuids: list)` | Aggregate content from multiple chapters with instructions for bible extraction |

### Prompts

| Tool | Signature | Description |
|---|---|---|
| `save_prompt` | `(name, content)` | Save a reusable prompt |
| `get_prompt` | `(name)` | Retrieve a prompt |
| `list_prompts` | `()` | List available prompts |

### World

| Tool | Signature | Description |
|---|---|---|
| `save_world` | `(section, content)` | Write a world section. Valid sections: `synthesis`, `bible`, `style`, `structure`, `plan`, `timeline`, `relations`. |
| `get_world` | `(section="")` | Read one section or all sections concatenated |
| `save_character` | `(name, content)` | Save a character profile |
| `get_character` | `(name)` | Retrieve a character profile |
| `list_characters` | `()` | List available character names |
| `save_location` | `(name, content)` | Save a location profile |
| `get_location` | `(name)` | Retrieve a location profile |
| `list_locations` | `()` | List available location names |

### Story state

| Tool | Signature | Description |
|---|---|---|
| `save_story_state` | `(chapter, situation, characters, knowledge, inventory)` | Archive current state under `chapter-NN/` and update `current/` |
| `get_story_state` | `(chapter=0)` | Read current state (0) or a specific chapter snapshot |
| `list_story_states` | `()` | List all archived chapter snapshots |

### Drafts

| Tool | Signature | Description |
|---|---|---|
| `save_brainstorm` | `(chapter, content)` | Save brainstorm notes for a chapter |
| `save_beats` | `(chapter, content)` | Save scene beats for a chapter |
| `save_draft` | `(chapter, content)` | Save AI-generated prose for a chapter |
| `get_draft` | `(chapter)` | Retrieve the AI draft for a chapter |

### Scene registry

| Tool | Signature | Description |
|---|---|---|
| `rebuild_scene_registry` | `()` | Force a full rebuild of `scene_registry.json` from the current project state. Use once to bootstrap, or anytime to force a refresh. |
| `get_scene_registry` | `(uuid="")` | Return the full registry JSON, or a single scene entry when `uuid` is provided. |

---

## 8. AI Agents

Agents are Claude Code sub-agents defined in `.claude/agents/`. They are invoked automatically by Claude based on context; the user does not need to name them explicitly.

### `brainstorm-agent`

**When:** Planning the next chapter.

Loads world context + current state, then engages in structured dialogue: raises continuity risks, surfaces open hooks, checks against `world/plan.md` for what must happen and what must NOT yet be revealed. Saves decisions to `drafts/chapter-NN/brainstorm.md`.

### `draft-agent`

**When:** Brainstorm notes are saved and a prose draft is needed.

Reads brainstorm notes, world context, and state. Phase 1: writes 5–8 scene beats and asks for confirmation. Phase 2: writes full chapter prose following the approved beats and `world/style.md`. Saves to `drafts/chapter-NN/draft.md`.

### `review-agent`

**When:** The author has finished rewriting in Scrivener.

Reads the chapter by UUID. Runs 5 checks: rhythm, character voices, dialogue quality, show-vs-tell, and continuity (against `state/current/` and `world/timeline.md`). Assigns a score /10. Then saves: review, summary, 7 metadata fields, a new state snapshot, and updates `world/plan.md`. Focused and fast — for full world enrichment use `scene-chronicler`.

### `scene-chronicler`

**When:** Bootstrapping existing scenes, or when deep enrichment is needed.

6-step pipeline, each step confirmed before continuing:
1. **Summary** — structured narrative summary
2. **Metadata** — 7 Scrivener metadata fields
3. **Character sheets** — create or enrich per character physically present
4. **Location sheets** — create or enrich per location
5. **Style analysis** — 5-point review + score
6. **World files** — update only the files actually touched by this scene (`plan`, `timeline`, `relations`, `bible` as applicable)

---

## 9. Code Style

### Environment

- Virtual environment at `.venv/` (not committed).
- Dependencies in `pyproject.toml`.

### Python conventions

- **All imports at the top of the file.** No imports inside functions except `TYPE_CHECKING` guards to break circular dependencies.
- **No class definitions in `__init__.py`.** Use `__init__.py` only to re-export symbols from submodules.
- **Complete type annotations on every function.** Parameters and return types are mandatory. Use `Optional[T]` for nullable, `None` for void.

```python
# ✅
def find_item(uuid: str) -> Optional[BinderNode]: ...

# ❌ — missing annotations
def find_item(uuid): ...
```

- **Dependency injection via constructor.** Never instantiate dependencies inside a class body; always accept them as `__init__` parameters. This makes all managers testable without patching globals.

```python
# ✅
class SummaryManager(BaseSceneDataManager):
    def __init__(self, project_path: Path, config: ProjectConfig, binder_map: Optional[dict]):
        super().__init__(project_path, config.summaries_subfolder, config, binder_map)

# ❌
class SummaryManager:
    def __init__(self, project_path: Path):
        self.config = ProjectConfig.default()   # hardcoded
```

- **No comments explaining what the code does.** Add a comment only when the WHY is non-obvious (a hidden constraint, a workaround, a subtle invariant).

### Error handling

- Managers raise on genuine errors (file not found, bad UUID).
- `ScrivenerProject` methods may catch and re-raise with context.
- `server.py` tools always catch and return a user-facing error string — never let an exception surface as an MCP protocol error.
- Best-effort operations (e.g. scene registry rebuild) catch all exceptions, log a warning, and continue without raising.

---

## 10. Testing Strategy

### Stack

- `pytest` with a `tests/fixtures/sample.scriv/` fixture project.
- Tests that write to disk use `tmp_path` (pytest's built-in temp directory).
- No mocking of the file system — tests use real files with real managers. Mocks are reserved for external I/O that can't run locally.

### Test types

| Type | Scope | What to test |
|---|---|---|
| **Unit** | Single class/function | Parsing logic, data transforms, manager methods in isolation |
| **Integration** | `server.py` tool + full project | End-to-end: call a tool, verify the file written on disk |

### Test isolation rules

- Copy the fixture with `shutil.copytree(SAMPLE_SCRIV, tmp_path / "test.scriv")` before any write test.
- Each test sets up its own state. No test relies on state left by another.
- Server-level tests reset `server.current_project` via `set_project_path()` in the fixture.

### Conventions

```python
# Fixture pattern for server tests
@pytest.fixture
def temp_project_server(tmp_path):
    dest = tmp_path / "temp.scriv"
    shutil.copytree(SAMPLE_SCRIV, dest)
    set_project_path(str(dest))
    return dest
```

- Test names describe behavior: `test_save_review_triggers_registry_rebuild`, not `test_save_review`.
- One assertion per concept. Split edge cases into separate test functions.
- Coverage is validated by running `pytest tests/` — all 88 tests must pass before any merge.

---

## 11. Security & Boundaries

| Constraint | Detail |
|---|---|
| **Local only** | No data leaves the machine. No network calls. |
| **Manuscript read-only** | `content.rtf`, `notes.rtf`, `synopsis.txt` are never written. |
| **`.scrivx` write scope** | Only the `<CustomMetaData>` section is modified. Scrivener's core structure is never touched. |
| **Backups before `.scrivx` writes** | `MetadataManager` creates a rolling backup (`project.scrivx.bak.1` … `.bak.5`) before every save. |
| **Path validation** | `set_project_path` validates: path exists, is a directory, ends in `.scriv`, contains a `.scrivx` file. |
| **Atomic writes** | All JSON and markdown outputs are written to a `.tmp` file then renamed with `os.replace()`. |
| **Registry rebuild is non-blocking** | A failed registry rebuild never prevents `update_metadata`, `save_summary`, or `save_review` from succeeding. |
| **No Research/Trash in registry** | Only `Text`-type nodes are included in `scene_registry.json`. |
