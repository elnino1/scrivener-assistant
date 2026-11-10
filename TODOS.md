# TODOs

Roadmap for the author-voice feature. Design: [docs/superpowers/specs/2026-11-10-author-voice-design.md](docs/superpowers/specs/2026-11-10-author-voice-design.md).

## Done

- [x] **Phase 1 — Measure**: `voice_stats`, `compare_voice_stats`, `compute_voice_baseline`,
      `compute_rewrite_diff`, `resolve_chapter_scenes`, `voice/` storage.
- [x] `voice-bootstrap` exposed as an MCP prompt (works in Claude Desktop).
- [x] Bootstrap run on the human-written corpus ("Celestia" + first 5 sections of "La découverte de Vee").

## Next — author

- [ ] Review `.ai-assistant/voice/guide.md`: drop moves that feel wrong, add missing ones,
      check the banned list. The bootstrap guide is a model's reading of the text; the author's
      review is what makes it a reference.

## Decisions

- [x] Drafts are written in **Claude Desktop** → phase 2 converts `brainstorm-agent`, `draft-agent`
      and `review-agent` to MCP prompts (instructions in `src/scrivener_assistant/agent_prompts/`),
      like `voice-bootstrap`; the Claude Code agent files become thin wrappers.
- Existing drafts after the corpus (rest of the "Hope" section) were written months ago in Claude
  Desktop and **mix author and Claude text**, with no saved `draft.md`. They are neither human
  corpus nor diffable drafts: the learning loop starts with the next chapter drafted through the
  new workflow.

## Phase 2 — Learn (close the loop)

- [ ] `handoff_draft(chapter)` tool: freeze `draft.md` into `draft.sent.md`, the diff baseline.
- [ ] `voice-learner` MCP prompt, run after retouching a chapter:
  - [ ] `compute_rewrite_diff`, then classify each edit: voice / structure / tic / plot / fidelity
        (only voice, structure and tic feed the voice model);
  - [ ] derive candidate rules into `hypotheses.md` (statement, kind, evidence, chapters seen / contradicted);
  - [ ] promotion: seen in ≥ 3 chapters and never contradicted → `guide.md`;
        demotion: contradicted in 2 chapters → back to `hypotheses.md`;
  - [ ] add strong author passages to `exemplars/`;
  - [ ] append a row to `ledger.md` and refresh `baseline.json`.
- [ ] `get_brainstorm(chapter)` tool, and fix `draft-agent` "On start" step 4 (it uses `get_draft`).
- [ ] Convert the writing-workflow agents (`brainstorm`, `draft`, `review`, `scene-chronicler`) to MCP prompts.
- [ ] Idea — **voice audit** of mixed sections: run `compare_voice_stats` paragraph by paragraph on
      the existing mixed drafts and flag the passages furthest from the baseline (likely Claude
      text) so the author knows where to retouch. Does not feed the learning loop.

## Phase 3 — Write better

- [ ] `voice-judge` MCP prompt: score ~10 voice dimensions (1–5, quoted evidence), top 3 fixes,
      max 3 rounds; runs on a different model from the writer.
- [ ] Sealed predictions: at hand-off, write `predictions.md` (5–15 expected edits), not shown to
      the author; `voice-learner` scores them → prediction hit rate.
- [ ] `[AUTEUR: …]` placeholders in `draft-agent` for what brainstorm/beats don't settle
      (feelings, opinions, key images) — the diff already treats them as fill-ins.
- [ ] `draft-agent` reads `voice/guide.md` and 3–5 matching exemplars before writing.
- [ ] `review-agent` / `scene-chronicler`: rhythm and show-vs-tell checks use `compare_voice_stats`.

## Housekeeping

- [ ] Update agent models (`claude-opus-4-7`, `claude-sonnet-4-6`) to current ones.
- [ ] Chapter numbering assumes chapters are top-level children of the manuscript folder; support
      Part → Chapter binders if needed.
- [ ] Tense heuristics: consider a better passé simple detection (3rd-person singular is skipped today).
