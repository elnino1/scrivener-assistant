# Writing Workflow Design

**Date:** 2026-04-20
**Status:** Approved

## Overview

Expand scrivener-assistant-mcp from a feedback/analysis tool into a full writing companion. The assistant supports a 5-stage per-chapter workflow: brainstorm → AI draft → human rewrite → AI review → human correction.

Inspired by the Claude-Book multi-agent framework, adapted for interactive use via MCP and Claude Code.

---

## Workflow

```
brainstorm-agent  →  draft-agent  →  [human rewrites in Scrivener]  →  review-agent  →  [human corrects]
```

Each chapter follows this cycle. The review agent closes the loop by updating versioned state, which feeds the next brainstorm session.

---

## Storage Structure

All new files live inside the existing `.ai-assistant/` folder within the `.scriv` bundle.

```
.ai-assistant/
├── world/                     # EXISTING + EXTENDED — single source of truth for all story knowledge
│   ├── synthesis.md           # quick-reference context, loaded first each session (existing)
│   ├── bible.md               # universe rules and established facts (existing)
│   ├── style.md               # POV, tense, tone, vocabulary rules (existing)
│   ├── structure.md           # narrative arc, themes (existing)
│   ├── plan.md                # chapter-by-chapter outline (existing)
│   ├── timeline.md            # chronological event log (existing)
│   ├── characters/            # MOVED — one file per character (was .ai-assistant/characters/)
│   └── locations/             # MOVED — one file per location (was .ai-assistant/locations/)
│
├── state/                     # NEW — versioned per-chapter state
│   ├── current/               # always reflects the latest completed chapter
│   │   ├── situation.md       # open story hooks, immediate context
│   │   ├── characters.md      # emotional/positional state of each character
│   │   ├── knowledge.md       # what each character knows at this point
│   │   └── inventory.md       # object locations and ownership
│   └── chapter-NN/            # archived snapshot per completed chapter
│       └── ...same 4 files
│
├── drafts/                    # NEW — working files per chapter
│   └── chapter-NN/
│       ├── brainstorm.md      # notes from the brainstorm session
│       ├── beats.md           # scene-by-scene plan (5–8 beats)
│       └── draft.md           # AI-generated prose
│
├── prompts/                   # existing
├── summaries/                 # existing
└── reviews/                   # existing (versioned, timestamped)
```

**Principles:**
- `world/` is the single source of truth for all story knowledge — always human-editable, never auto-overwritten
- `state/` is auto-updated by review-agent but also human-editable
- `drafts/` is working scratch space, never treated as read-only
- Chapter folders use zero-padded numbers: `chapter-05`, `chapter-12`

**Migration required:**
- Move `.ai-assistant/characters/` → `.ai-assistant/world/characters/`
- Move `.ai-assistant/locations/` → `.ai-assistant/world/locations/`
- Update `character_manager.py` and `location_manager.py` in the MCP server to use the new paths
- All existing character and location files are kept as-is, only the folder path changes

---

## New MCP Tools (10)

### World tools
| Tool | Description |
|------|-------------|
| `get_world(section?)` | Read any section of `world/` (style, bible, structure, plan, timeline, synthesis) or the full world context. Used by all agents on start. |
| `save_world(section, content)` | Write/update a world section. Accepts: style, bible, structure, plan, timeline, synthesis. |

### State tools
| Tool | Description |
|------|-------------|
| `get_story_state(chapter?)` | Get current state (all 4 files) or a specific archived chapter's state. |
| `save_story_state(chapter, situation, characters, knowledge, inventory)` | Create a new state snapshot, archive the previous current. |
| `list_story_states()` | List all archived chapter state snapshots. |

### Draft tools
| Tool | Description |
|------|-------------|
| `save_brainstorm(chapter, content)` | Save notes from the brainstorm session. |
| `save_beats(chapter, content)` | Save the scene-by-scene plan. |
| `save_draft(chapter, content)` | Save AI-written prose. |
| `get_draft(chapter)` | Read an AI draft (used by the user to review and copy into Scrivener before rewriting). |

### Extraction tool
| Tool | Description |
|------|-------------|
| `extract_bible_from_chapters(uuids)` | Read a list of Scrivener documents and return a structured analysis (style patterns, character appearances, locations, narrative arc). Does not auto-save — user reviews and confirms before writing to bible files. |

---

## Agent Definitions

Three agents in `.claude/agents/`, each mapping to one phase.

### `brainstorm-agent` (Sonnet)

**Purpose:** Help plan the next chapter(s) through dialogue.

**Reads on start:** full world context, current state, last 2 chapter summaries.

**Behavior:**
- Conversational: asks about the user's intentions, raises continuity risks, suggests plot directions
- Flags character knowledge gaps (e.g. "Character X doesn't know Y yet")
- Surfaces open story hooks from `state/current/situation.md`
- When the user is satisfied, saves notes to `drafts/chapter-NN/brainstorm.md`

---

### `draft-agent` (Opus)

**Purpose:** Produce beats and prose for the next chapter.

**Reads on start:** brainstorm notes, full world context, current state.

**Two internal phases:**
1. **Beats** — creates 5–8 scene beats respecting style + continuity, saves to `drafts/chapter-NN/beats.md`
2. **Prose** — writes draft following beats and style guide, saves to `drafts/chapter-NN/draft.md`

No validation gates — drafts once. The human then rewrites in Scrivener.

---

### `review-agent` (Sonnet)

**Purpose:** Review the human-rewritten chapter and update story state.

**Reads on start:** the Scrivener document (by UUID), full world context, current state.

**Three sequential checks:**
1. Style consistency — checks against `world/style.md`
2. Character authenticity — checks against `world/characters/` and `state/current/characters.md`
3. Continuity — checks timeline, locations, knowledge boundaries against `state/current/`

**Outputs:**
- Saves structured review to `reviews/` (existing versioned system)
- Always saves a new `state/chapter-NN/` snapshot and updates `state/current/` — regardless of issues found. The user can re-run after corrections.
- Prompts user to update `world/characters/` or `world/locations/` if new entities appeared

---

## Bootstrap (One-Time Setup)

For the current project, `world/` files already exist and are the starting point:

1. Move `.ai-assistant/characters/` → `.ai-assistant/world/characters/`
2. Move `.ai-assistant/locations/` → `.ai-assistant/world/locations/`
3. Manually create `state/current/` to reflect where the story currently stands (draw from `world/synthesis.md` as a starting point)
4. From that point on, `review-agent` keeps state updated automatically

For future projects starting from scratch, call `extract_bible_from_chapters(uuids)` on existing chapters, review the output, and save to `world/` files before creating `state/current/`.

---

## Error Handling

- If `state/current/` does not exist when brainstorm-agent starts, it prompts the user to either run the bootstrap or create state manually
- If brainstorm notes don't exist when draft-agent starts, it asks the user to run brainstorm-agent first or confirm they want to skip
- If the Scrivener UUID is not found when review-agent starts, it reports which UUIDs are available in the binder

---

## Out of Scope

- Writing directly into Scrivener's binder (drafts go to `.ai-assistant/drafts/`, not into `.scrivx`)
- Ebook generation
- AI-detection reduction (perplexity improver)
- Automatic chapter iteration loops (no retry-on-fail; human drives corrections)
