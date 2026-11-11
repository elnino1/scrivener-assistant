# TODOs

Roadmap for the author-voice feature. Design: [docs/superpowers/specs/2026-11-10-author-voice-design.md](docs/superpowers/specs/2026-11-10-author-voice-design.md).

## Resume here (last update: 2026-11-11)

- **Claude Code session**: `83465f4f-af6f-46b3-8b98-35a26ee829b8` — run
  `claude --resume 83465f4f-af6f-46b3-8b98-35a26ee829b8` from this repo on the host (not in the
  devcontainer: sessions are stored per working directory under `~/.claude/projects/`).
  If the session is gone, this file + the design spec are enough to restart.
- **Branch**: `learn_write`, pushed; PR [#17](https://github.com/elnino1/scrivener-assistant/pull/17)
  to `main` is open and not merged.
- **State**: phase 1 done and shipped in a local `.mcpb` (installed in Claude Desktop);
  `voice-bootstrap` was run on the corpus, `voice/` exists in the project.
- **Done 2026-11-11**: voice audit of the mixed "Hope" scenes (one-off script, report given to the
  author); `handoff_draft` implemented; chapter 2 "Hope" frozen with `source="scrivener"`
  (18 non-empty scenes, `kind: legacy-mixed`).
- **Next**: the author retouches "Hope" in Scrivener; meanwhile, build the `voice-learner` MCP prompt
  and test it on that chapter's diff (weak evidence: hypotheses only, no promotion).
- **Server not rebuilt yet**: the installed `.mcpb` does not have `handoff_draft`.
- **After any server change**: `uv run --extra dev pytest`, rebuild with
  `npx -y @anthropic-ai/mcpb pack . scrivener-assistant-dev.mcpb`, uninstall the old extension in
  Claude Desktop, install the new one, re-set the project path.
- **Conventions**: agent instructions live in `src/scrivener_assistant/agent_prompts/*.md` and are
  exposed as MCP prompts in `src/server.py` (`# --- Prompts ---`); new tools must also be listed in
  `manifest.json`.

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
