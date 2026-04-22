# Writing Workflow — User Guide

This guide covers the full writing workflow: from first-time setup to the per-chapter cycle of brainstorming, drafting, reviewing, and maintaining world continuity.

---

## Overview

The assistant supports a 5-stage per-chapter workflow:

```
brainstorm-agent → draft-agent → [you rewrite in Scrivener] → review-agent → [you correct]
```

Between chapters, the assistant maintains a versioned **story state** (who knows what, who is where, what objects exist) and a **world bible** (style rules, universe facts, character and location profiles). These feed each new brainstorm session automatically.

For retrospective processing of existing scenes, use **`scene-chronicler`** — it extracts all world data from any scene in a single pipeline.

---

## Storage Structure

Everything lives inside `.ai-assistant/` within your `.scriv` bundle. Your manuscript files are never touched.

```
.ai-assistant/
├── world/                  ← source of truth for all story knowledge (human-editable)
│   ├── _synthèse.md        quick-reference context loaded at the start of each session
│   ├── bible.md            universe rules and established facts
│   ├── style.md            POV, tense, rhythm, vocabulary rules
│   ├── structure.md        narrative arc and themes
│   ├── plan.md             chapter-by-chapter outline with [WRITTEN]/[PLANNED]/[CONSIDERED] status
│   ├── timeline.md         chronological event log
│   ├── relations.md        character relationship map
│   ├── characters/         one .md file per character
│   └── locations/          one .md file per location
│
├── state/                  ← versioned per-chapter snapshots (auto-updated by review-agent)
│   ├── current/            always reflects the latest completed chapter
│   │   ├── situation.md    open story hooks, immediate context
│   │   ├── characters.md   emotional/positional state of each character
│   │   ├── knowledge.md    what each character knows at this point
│   │   └── inventory.md    object locations and ownership
│   └── chapter-05/         archived snapshot (one per completed chapter)
│
├── drafts/                 ← working files per chapter (scratch space)
│   └── chapter-06/
│       ├── brainstorm.md   notes from the brainstorm session
│       ├── beats.md        scene-by-scene plan
│       └── draft.md        AI-generated prose
│
├── reviews/                versioned style reviews (timestamped)
├── summaries/              scene summaries
└── prompts/                reusable analysis prompts
```

**Key principles:**
- `world/` is always human-editable — the agents read it but never overwrite it without showing you first
- `state/` is auto-updated by `review-agent` after each chapter, but you can edit it manually too
- `drafts/` is scratch space — AI-generated content you copy into Scrivener and rewrite freely

---

## First-Time Setup (Bootstrap)

If you already have written chapters in Scrivener:

**Step 1 — Extract your world data**

Ask Claude to run `extract_bible_from_chapters` on your existing chapters. This reads them and returns a structured analysis covering style patterns, characters, locations, and narrative arc. Review the output and save each section:

```
save_world("style", <content>)
save_world("bible", <content>)
save_character("CharacterName", <content>)
save_location("LocationName", <content>)
```

**Step 2 — Create the initial state**

Create `state/current/` manually (or ask Claude to draft it from your `world/_synthèse.md`):

- `situation.md` — where does the story stand right now? What hooks are open?
- `characters.md` — where is each character emotionally and physically?
- `knowledge.md` — what does each character know at this point?
- `inventory.md` — where are the key objects?

You can also call `save_story_state(0, ...)` with chapter=0 to initialize without archiving.

**Step 3 — Process existing scenes (optional)**

Run `scene-chronicler` on any existing chapter to generate summaries, metadata, character sheets, and update world files — without the quality review loop.

From that point on, `review-agent` keeps state updated automatically after each new chapter.

---

## Per-Chapter Workflow

### Stage 1 — Brainstorm

**When:** You want to plan the next chapter.

**How:** In Claude Code, type:
> "Plan chapter 6" or just describe what you have in mind.

Claude will automatically use `brainstorm-agent`, which:
1. Loads your full world context and current state
2. Silently checks `world/plan.md` for what must happen and what must NOT be revealed yet
3. Asks what you have in mind, then engages in dialogue:
   - Raises continuity risks
   - Surfaces open hooks from the current state
   - Suggests plot directions if you're open to ideas
   - Pushes back if your ideas conflict with the plan or risk premature reveals
4. When you're satisfied, summarizes decisions and saves to `drafts/chapter-06/brainstorm.md`

---

### Stage 2 — AI Draft

**When:** Brainstorm notes are saved and you want a first draft.

**How:** Ask Claude to draft the chapter.

Claude will use `draft-agent`, which:
1. Reads brainstorm notes, world context, and current state
2. **Phase 1 — Beats:** Writes 5–8 scene beats (what happens, who drives, emotional note). Shows you the beats and asks for confirmation before continuing.
3. **Phase 2 — Prose:** Writes the full chapter following the approved beats and style guide. Saves to `drafts/chapter-06/draft.md`.
4. **Phase 3 — TODOs (optional):** If the draft contains `[TODO: ...]` markers, fills them in with style-matched content.

The draft is saved as a file — you copy it into Scrivener yourself.

---

### Stage 3 — Human Rewrite

Copy the draft into Scrivener and rewrite freely. The AI draft is a starting point, not a final product. Take ownership of the prose.

---

### Stage 4 — Review

**When:** You've finished rewriting in Scrivener and want feedback.

**How:** Give Claude the Scrivener UUID of your chapter.

Claude will use `review-agent`, which:
1. Reads your chapter directly from Scrivener
2. Runs 5 checks:
   - **Rhythm** — sentence variation, pacing balance
   - **Character voices** — distinct voices, register consistency
   - **Dialogue quality** — advancing plot, no artificial exposition
   - **Show vs tell** — emotional labeling vs sensory grounding
   - **Consistency** — factual continuity, knowledge violations, timeline
3. Assigns a **score /10** with justification
4. Saves a **structured summary** (narrative + key plot points + emotional close)
5. Saves **7 metadata fields** to Scrivener (Characters present, Locations, Plot, Emotional arc, Philosophy, Tension, Score)
6. Updates `world/plan.md` — marks the chapter as written, checks for premature reveals
7. Saves a new **state snapshot** to `state/chapter-06/` and updates `state/current/`

If new characters or locations appeared, it prompts you to save their profiles.

---

### Stage 5 — Correct

Review the feedback and make corrections in Scrivener. If significant changes were made, run `review-agent` again. The previous review is automatically archived — you can always compare with `get_previous_review`.

When you're satisfied, the chapter is done. The state in `state/current/` is now the starting point for the next brainstorm session.

---

## Retrospective Enrichment — scene-chronicler

Use `scene-chronicler` when you want to thoroughly process any scene — not for the writing loop, but to enrich world data from existing content.

**When to use it:**
- During bootstrap, to process chapters you wrote before setting up the assistant
- Anytime after writing a scene to fully update all world files
- When you want character sheets, location sheets, and world updates all in one pass

**What it does (6 steps):**
1. **Summary** — structured narrative summary + key plot points, saved via `save_summary`
2. **Metadata** — 7 fields extracted and saved via `update_metadata`
3. **Character sheets** — created or enriched for every character present
4. **Location sheets** — created or enriched for every setting
5. **Style analysis** — 5-point quality analysis + score/10 + `save_review`
6. **World files** — updates `plan.md`, `timeline.md`, `relations.md`, `bible.md` as needed

It reads the document once and processes everything sequentially. Each step is confirmed before continuing.

---

## Agents Quick Reference

| Agent | When to use | What it does |
|-------|-------------|--------------|
| `brainstorm-agent` | Before writing a chapter | Dialogue to plan direction, continuity checks, saves brainstorm notes |
| `draft-agent` | After brainstorm | Beats → prose → TODO filling, saves to `drafts/` |
| `review-agent` | After human rewrite | 5-point review, score, summary, metadata, state update, plan update |
| `scene-chronicler` | Bootstrap or deep enrichment | Full 6-step pipeline: summary, metadata, character sheets, location sheets, style review, world files |

**`review-agent` vs `scene-chronicler`:**
- `review-agent` is for the writing loop — fast, focused on quality feedback and keeping state current
- `scene-chronicler` is for comprehensive data extraction — slower, extracts everything from any scene

---

## Tips

**Editing world files manually**
Open any file in `world/` directly in your text editor. The agents re-read them at the start of each session. Your edits take effect immediately.

**Recovering from a bad state update**
The previous state is always archived. Check `list_story_states()` and `get_story_state(<chapter>)` to retrieve any snapshot.

**Reviewing the review history**
Use `get_review_history(<uuid>)` to see all past reviews for a chapter, and `get_previous_review(<uuid>)` to compare your current version against the last feedback.

**Skipping brainstorm**
You can run `draft-agent` without prior brainstorm notes — it will warn you and ask for confirmation. Useful when you know exactly what you want to write.

**Triggering agents in Claude Code**
Agents are invoked automatically when you describe what you want to do. You don't need to name them explicitly:
- "Let's plan chapter 7" → `brainstorm-agent`
- "Draft it" → `draft-agent`
- "Review chapter 6, UUID is ABC123" → `review-agent`
- "Process this existing scene, UUID is XYZ" → `scene-chronicler`
