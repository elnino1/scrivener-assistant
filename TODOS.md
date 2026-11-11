# TODOs

Roadmap for the author-voice feature. Design: [docs/superpowers/specs/2026-11-10-author-voice-design.md](docs/superpowers/specs/2026-11-10-author-voice-design.md).

## Resume here (last update: 2026-11-11)

- **Claude Code session**: `ce5fd8b3-8451-4dad-95ec-917103de18e8` (previous: `83465f4f-…`) — run
  `claude --resume ce5fd8b3-8451-4dad-95ec-917103de18e8` from this repo on the host (not in the
  devcontainer: sessions are stored per working directory under `~/.claude/projects/`).
  If the session is gone, this file + the design spec are enough to restart.
- **Branch**: `learn_write`, pushed; PR [#17](https://github.com/elnino1/scrivener-assistant/pull/17)
  to `main` is open and not merged.
- **State**: phases 1 and 2 shipped (except prediction scoring); the rebuilt `.mcpb` (with
  `handoff_draft` and the `voice-learner` prompt) is installed in Claude Desktop.
- **Project data (`Mere.scriv/.ai-assistant/`)**:
  - `voice/guide.md` reviewed by the author; `voice/baseline.json` = 25 human scenes, now with
    `source_uuids`; `voice/exemplars/` = 17 exemplars (15 approved picks + `description-04`,
    `action-04` chosen by the author).
  - `voice/audit-hope-2026-11-11.md`: voice audit of the mixed "Hope" scenes (which passages to
    retouch first). Caveat: « quelque chose », « un instant », « soudain » also occur in the
    author's corpus (32 / 9 / 9), so they only signal overuse; em dashes in narration (author: 0)
    are the reliable AI marker.
  - Chapter 2 "Hope" is frozen (`drafts/chapter-02/draft.sent.md` + `handoff.json`,
    `kind: legacy-mixed`, 18 non-empty scenes; the 4 empty scenes are excluded from the diff).

### Next steps

1. **Author**: retouch "Hope" in Scrivener (guided by the audit). Do not re-run `handoff_draft`
   on chapter 2: it would reset the baseline of the diff.
2. **Author, in Claude Desktop**: run the `voice-learner` prompt with `chapter = 2`. Expect a long
   classification (many pairs); results are weak evidence (hypotheses only, no promotion).
3. **Then, together**: review the hypotheses it produced and the prompt's behaviour; adjust
   `agent_prompts/voice_learner.md` if needed.
4. **Then phase 3** (below), starting with `draft-agent` reading `guide.md` + exemplars, and
   `[AUTEUR: …]` placeholders; the next new chapter goes through `handoff_draft` (source `draft`).

### Reminders

- **After any server change**: `uv run --extra dev pytest`, rebuild with
  `npx -y @anthropic-ai/mcpb pack . scrivener-assistant-dev.mcpb`, uninstall the old extension in
  Claude Desktop, install the new one, re-set the project path.
- **Conventions**: agent instructions live in `src/scrivener_assistant/agent_prompts/*.md` and are
  exposed as MCP prompts in `src/server.py` (`# --- Prompts ---`); new tools must also be listed in
  `manifest.json`.
- **Decisions (2026-11-11)**: guide changes only after author approval; the baseline grows only
  with whole scenes written by hand, never with retouched AI text; `legacy-mixed` chapters never
  count toward promotion.

## Done

- [x] **Phase 1 — Measure**: `voice_stats`, `compare_voice_stats`, `compute_voice_baseline`,
      `compute_rewrite_diff`, `resolve_chapter_scenes`, `voice/` storage.
- [x] `voice-bootstrap` exposed as an MCP prompt (works in Claude Desktop).
- [x] Bootstrap run on the human-written corpus ("Celestia" + first 5 sections of "La découverte de Vee").

## Next — author

- [x] Review `.ai-assistant/voice/guide.md` (2026-11-11): open points resolved (tense aligned with
      the corpus in `style.md`; two timelines, Célestia 2057 then Hope 2066).

## Decisions

- [x] Drafts are written in **Claude Desktop** → phase 2 converts `brainstorm-agent`, `draft-agent`
      and `review-agent` to MCP prompts (instructions in `src/scrivener_assistant/agent_prompts/`),
      like `voice-bootstrap`; the Claude Code agent files become thin wrappers.
- Existing drafts after the corpus (rest of the "Hope" section) were written months ago in Claude
  Desktop and **mix author and Claude text**, with no saved `draft.md`. They are neither human
  corpus nor diffable drafts: the learning loop starts with the next chapter drafted through the
  new workflow.

## Phase 2 — Learn (close the loop)

- [x] `handoff_draft(chapter, source, overwrite)` tool: freeze `draft.md` into `draft.sent.md`, the diff baseline (plus `handoff.json`). `source="scrivener"` freezes the current Scrivener text for legacy mixed chapters (kind `legacy-mixed`, weak evidence).
- [x] `voice-learner` MCP prompt, run after retouching a chapter (author validates every write to `guide.md`):
  - [x] `compute_rewrite_diff`, then classify each edit: voice / structure / tic / plot / fidelity
        (`get_rewrite_edits` / `save_edit_labels`, labels persist across diff re-runs;
        only voice, structure and tic feed the voice model);
  - [x] derive candidate rules into `hypotheses.md` (statement, kind, evidence, chapters seen / contradicted);
  - [x] promotion: seen in ≥ 3 chapters (legacy-mixed excluded) and never contradicted → `guide.md`
        (`ban` needs `count_in_corpus` = 0); demotion: contradicted in 2 chapters;
  - [x] add strong author passages to `exemplars/`;
  - [x] append a row to `ledger.md`; baseline grows only with author-written text, after approval
        (never with retouched AI text);
  - [ ] score predictions (needs phase 3 `predictions.md`).
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
