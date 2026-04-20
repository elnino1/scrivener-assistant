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
├── bible/
│   ├── style.md               # POV, tense, tone, vocabulary rules
│   ├── structure.md           # narrative arc, themes, chapter count
│   ├── characters/            # one file per character (existing, promoted)
│   └── locations/             # one file per location (existing, promoted)
│
├── state/
│   ├── current/               # always reflects the latest completed chapter
│   │   ├── situation.md       # open story hooks, immediate context
│   │   ├── characters.md      # emotional/positional state of each character
│   │   ├── knowledge.md       # what each character knows at this point
│   │   └── inventory.md       # object locations and ownership
│   └── chapter-NN/            # archived snapshot per completed chapter
│       └── ...same 4 files
│
├── drafts/
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
- `bible/` is the source of truth — always human-editable
- `state/` is auto-updated by review-agent but also human-editable
- `drafts/` is working scratch space, never treated as read-only
- Existing `characters/` and `locations/` files stay at their current paths (`.ai-assistant/characters/`, `.ai-assistant/locations/`); they are logically part of the bible and included when `get_bible()` is called. No migration needed.
- Chapter folders use zero-padded numbers: `chapter-05`, `chapter-12`

---

## New MCP Tools (10)

### Bible tools
| Tool | Description |
|------|-------------|
| `get_bible(section?)` | Read style, structure, or full bible. Used by all agents as context. |
| `save_bible(section, content)` | Write/update a bible section (style or structure). |

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

**Reads on start:** full bible, current state, last 2 chapter summaries.

**Behavior:**
- Conversational: asks about the user's intentions, raises continuity risks, suggests plot directions
- Flags character knowledge gaps (e.g. "Character X doesn't know Y yet")
- Surfaces open story hooks from `state/current/situation.md`
- When the user is satisfied, saves notes to `drafts/chapter-NN/brainstorm.md`

---

### `draft-agent` (Opus)

**Purpose:** Produce beats and prose for the next chapter.

**Reads on start:** brainstorm notes, full bible, current state.

**Two internal phases:**
1. **Beats** — creates 5–8 scene beats respecting style + continuity, saves to `drafts/chapter-NN/beats.md`
2. **Prose** — writes draft following beats and style guide, saves to `drafts/chapter-NN/draft.md`

No validation gates — drafts once. The human then rewrites in Scrivener.

---

### `review-agent` (Sonnet)

**Purpose:** Review the human-rewritten chapter and update story state.

**Reads on start:** the Scrivener document (by UUID), full bible, current state.

**Three sequential checks:**
1. Style consistency — checks against `bible/style.md`
2. Character authenticity — checks against `bible/characters/` and `state/current/characters.md`
3. Continuity — checks timeline, locations, knowledge boundaries against `state/current/`

**Outputs:**
- Saves structured review to `reviews/` (existing versioned system)
- Always saves a new `state/chapter-NN/` snapshot and updates `state/current/` — regardless of issues found. The user can re-run after corrections.
- Prompts user to update `bible/characters/` or `bible/locations/` if new entities appeared

---

## Bootstrap (One-Time Setup)

For existing Scrivener projects:

1. Call `extract_bible_from_chapters(uuids)` on existing chapters
2. Review the output and save to `bible/style.md`, `bible/structure.md`, characters, locations
3. Manually create `state/current/` to reflect the current story situation
4. From that point on, `review-agent` keeps state updated automatically

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
