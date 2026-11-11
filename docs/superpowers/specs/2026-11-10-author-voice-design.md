# Author Voice Design

**Date:** 2026-11-10
**Status:** Draft

## Overview

Make AI drafts sound like the author, and make that get better with every chapter the author
retouches. Today the only style input is `world/style.md`: a short, prescriptive, static rule list.
Nothing compares the AI draft with the author's retouched version in Scrivener, so the system never
learns from the author's edits.

Inspired by Nat Eliason, "How to Build an AI Writing System That Actually Sounds Like You" (X article,
2026). The ideas reused here:

- separate **writer** and **judge**, with a short revision loop;
- **sealed predictions**: before the author sees a draft, the judge writes down the edits it expects;
  the share of real edits it predicted measures how well the system knows the voice;
- an **outer loop** that classifies the author's real edits and turns them into rules;
- rules learned from one edit are **hypotheses** until confirmed across several chapters
  (single-edit rules caused overshoot in the original system);
- a voice guide made of **descriptive moves + measurable stats + a narrow banned list**
  (only words the author never uses);
- an explicit **placeholder** for content the inputs don't contain, instead of inventing it;
- one headline metric: **edit rate** (share of the draft the author changed).

Working assumption, confirmed by the author: drafts are **retouched** in Scrivener, not rewritten
from scratch, so a sentence-level diff between draft and final text is meaningful.

---

## Workflow

```
brainstorm-agent → draft-agent ⇄ voice-judge → [author retouches in Scrivener] → voice-learner → review-agent
                                     │                                               │
                                     └── sealed predictions ────────────────────────►│
                                                                                     ▼
                                                            voice/ (guide, hypotheses, ledger)
                                                                                     │
                              draft-agent and voice-judge read it at the next chapter ◄┘
```

---

## Storage

New folder inside `.ai-assistant/`, next to `world/`:

```
.ai-assistant/
├── voice/
│   ├── guide.md            # confirmed rules: moves, banned list, stat targets, do/don't pairs
│   ├── hypotheses.md       # candidate rules with evidence and confirmation counts
│   ├── baseline.json       # voice_stats() of the human corpus (targets + tolerances)
│   ├── exemplars/          # short passages written by the author, tagged by kind
│   │   └── <slug>.md       #   (dialogue, action, interiority, description, transition)
│   ├── edits/
│   │   └── chapter-NN.json # output of compute_rewrite_diff + classification
│   └── ledger.md           # one row per chapter: edit rate, prediction hit rate, rules promoted
└── drafts/chapter-NN/
    ├── draft.md            # existing; may still be revised before hand-off
    ├── draft.sent.md       # NEW — frozen copy handed to the author (the diff baseline)
    ├── handoff.json        # NEW — hand-off record: source, kind, sent_at, frozen scenes
    ├── judge.md            # NEW — judge rounds: scores, evidence, top fixes
    └── predictions.md      # NEW — sealed predicted edits, written at hand-off
```

`world/style.md` stays as the author-owned, hand-written rule list. `voice/guide.md` is
system-maintained and may only be changed by the bootstrap or by promoting a hypothesis.

---

## Components

### 1. `voice_stats(text)` — deterministic metrics (Python)

No LLM. French-aware heuristics, computed on narration and dialogue separately:

- sentence length (mean, median, p10/p90), paragraph length in sentences and words;
- dialogue share (lines starting with `—`/`«`), dialogue tag variety;
- tense mix in narration: passé simple / imparfait / passé composé / présent (suffix heuristics);
- frequency per 1,000 words: `on`, `-ment` adverbs, exclamations, questions, ellipses, semicolons;
- sentence-opening variety (share of the top 5 first words);
- lexical density (type/token on a fixed window).

`compare_voice_stats(text)` returns each metric next to `baseline.json` with a within/outside
tolerance flag. Both are exposed as MCP tools.

### 2. `compute_rewrite_diff(chapter, uuids)` — draft vs final (Python)

- Baseline: `draft.sent.md`. Final: the Scrivener documents `uuids`, concatenated in binder order
  (one chapter draft may map to several Scrivener sections).
- Paragraph alignment, then sentence alignment (`difflib.SequenceMatcher`), then word-level ops.
- Output: word-level **edit rate**, counts of kept / modified / deleted / inserted sentences, and
  the list of edit pairs `{before, after, op, position}`.
- Saved to `voice/edits/chapter-NN.json`. Classification is added later by `voice-learner`.
- When `handoff.json` exists, the output carries its `kind` and `sent_at`, and the final text is
  limited to its `frozen_scenes` (if set).

### 2b. `handoff_draft(chapter, source, overwrite)` — freeze the diff baseline (Python)

- `source="draft"` (normal): copy `draft.md` to `draft.sent.md`; `kind: ai-draft`.
- `source="scrivener"` (legacy chapters drafted before this workflow, mixing author and AI text,
  never frozen): freeze the current Scrivener text of the chapter's **non-empty** scenes;
  `kind: legacy-mixed`. Scenes empty at hand-off are recorded out of `frozen_scenes`, so text
  written there later never counts as edits. Diffs of a `legacy-mixed` chapter are weak evidence:
  they may create or support hypotheses, never promote a rule on their own.
- Refuses to replace an existing `draft.sent.md` unless `overwrite=True`.
- Writes `handoff.json`: chapter, title, source, kind, `sent_at`, words, scenes, `frozen_scenes`.

### 3. `voice-judge` agent

Called by `draft-agent` after the prose phase. For each round (max 3):

1. Run `compare_voice_stats` on the draft.
2. Score ~10 voice dimensions from 1 to 5, each with a quoted line as evidence. Dimensions come
   from `voice/guide.md` (bootstrap seeds them: rhythm, sentence openings, interiority, sensory
   register, dialogue, tense discipline, use of `on`, transitions, endings of scenes, lexical
   singularity).
3. List the 3 worst lines and the **top 3 fixes**. `draft-agent` applies them and resubmits.

Stop when no dimension is below 4 or after round 3. Then, at hand-off:

- copy `draft.md` to `draft.sent.md`;
- write `predictions.md`: 5–15 concrete predicted edits (`"« … » → probably cut / rephrased because …"`),
  not shown to the author before retouching.

The judge runs on a different model from the writer (judge: Opus, writer: per `draft-agent`) so
it does not grade its own habits.

### 4. `[AUTEUR: …]` placeholders

`draft-agent` must not invent what the brainstorm notes and beats do not settle: a character's
private feeling, an opinion, an intimate detail, a key image. It writes `[AUTEUR: <what is needed>]`
instead. The diff tool treats placeholder replacements as **fill-ins**, not edits (excluded from the
edit rate, counted separately).

### 5. `voice-learner` agent

Run by the author after retouching a chapter, before `review-agent`:

1. `compute_rewrite_diff(chapter, uuids)`.
2. Classify each edit pair: `voice` (word choice, rhythm, register), `structure` (order, cuts,
   paragraphing), `fidelity` (fact / continuity fix), `plot` (story change), `tic` (AI-ism removed).
   Only `voice`, `structure` and `tic` feed the voice model.
3. Score `predictions.md` against the real edits → **prediction hit rate**.
4. Derive candidate rules. Each one goes to `hypotheses.md` with: statement, kind
   (`prefer`, `avoid`, `ban`, `stat`), before/after evidence, chapters seen, chapters contradicted.
5. **Promotion**: a hypothesis seen in ≥ 3 chapters and contradicted in none moves to `guide.md`.
   **Demotion**: a guide rule contradicted in 2 chapters goes back to `hypotheses.md`.
   A `ban` needs zero occurrences of the word in the human corpus.
6. Add strong human-written passages (heavily retouched or added) to `exemplars/`.
7. Append a row to `ledger.md` and update `baseline.json` with the retouched chapter.

### 6. `voice-bootstrap` (one-time)

Corpus written entirely by the author: the **"Celestia"** chapter and the **first 5 sections of
"La découverte de Vee"**.

1. `voice_stats` over the corpus → `baseline.json`.
2. Extract 8–12 characteristic moves with quoted examples → `guide.md`.
3. Build the banned list: common AI-isms in French fiction absent from the corpus.
4. Pick 10–15 exemplars covering each passage kind.
5. Seed the judge dimensions.

---

## Changes to existing agents

- **draft-agent**: read `voice/guide.md` and 3–5 exemplars matching the scene kinds before
  writing; run the `voice-judge` loop; use `[AUTEUR: …]` placeholders; write `draft.sent.md` at
  hand-off. Also fix the duplicated `save_draft` line and the `get_draft` check that looks for
  brainstorm notes.
- **review-agent / scene-chronicler**: Check 1 (rhythm) and Check 4 (show vs tell) use
  `compare_voice_stats` instead of free judgement.

---

## Metrics

Tracked per chapter in `ledger.md`, with a target trend rather than fixed thresholds:

| Metric | Meaning | Expected trend |
|---|---|---|
| Edit rate | share of `draft.sent.md` words the author changed (fill-ins excluded) | down |
| Prediction hit rate | share of real voice/structure edits that were predicted | up |
| Stat drift | metrics outside baseline tolerance | down |
| Rules | guide rules / open hypotheses | guide grows, then stabilises |

---

## Phases

1. **Measure** (implemented) — `voice_stats`, `compare_voice_stats`, `compute_rewrite_diff` + tests;
   `voice-bootstrap` on the corpus.
2. **Learn** — `voice-learner`, hypotheses/promotion, ledger; `draft.sent.md` hand-off.
3. **Write better** — `voice-judge` loop, sealed predictions, `[AUTEUR: …]` placeholders,
   `draft-agent` changes.

Phase 1 alone already gives a baseline and lets the author measure the current drafts.

## Agent instructions as MCP prompts

Agent instructions live in `src/scrivener_assistant/agent_prompts/<name>.md` (single source of
truth, shipped in the package and the `.mcpb` bundle) and are exposed as MCP prompts
(`@mcp.prompt` in `src/server.py`, loaded via `load_agent_prompt`) so they work in Claude Desktop,
where `.claude/agents/` is unavailable. The Claude Code subagent file only points to that file.
`voice-bootstrap` is done; the future `voice-learner` and `voice-judge` follow the same pattern.

## Open questions

- ~~Mapping chapter number → Scrivener UUIDs~~ — Resolved: derived from the scene registry (chapter = Nth top-level DraftFolder child holding text, or matched by title; see `resolve_chapter_scenes`). `compute_rewrite_diff` takes only `chapter`.
- Should the judge also run a blind A/B between two writer models on one scene, as in the original?
- Retention: keep every `edits/chapter-NN.json`, or summarise after promotion?
