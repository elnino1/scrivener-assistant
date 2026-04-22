# Scrivener Assistant: User Journey & Prompt Examples

> **This document covers the original read-and-analyze workflow.**
> For the full writing workflow with brainstorm/draft/review agents, see the **[User Guide](user_guide.md)**.

This guide demonstrates how to use the Scrivener Assistant to analyze and improve your writing project. It follows a typical workflow from connecting to a project to storing deep analysis in your metadata.

## Workflow Overview

1.  **Connect** to your project.
2.  **Explore** the binder structure.
3.  **Read** a specific scene or chapter.
4.  **Save** a reusable analysis prompt.
5.  **Analyze** the text and **Update** Scrivener metadata.

---

## Usage Paths: MCP vs CLI

This project can be used in two ways. The examples below show *both* methods for each step:
1. **MCP Client (e.g. Claude Desktop):** You chat naturally, and the model calls the "Tool Called" natively in the background.
2. **CLI (Terminal):** You or your AI Agent execute the explicit `scrivener-cli` commands in your terminal to achieve the same result.

---

## Step 1: Connect to Project

First, ensure the server knows which project to look at.

**User Prompt:**
> "Connect to my Scrivener project at `/Users/me/Documents/MyNovel.scriv`"

**MCP Tool Called:** `set_project_path`

*(**CLI Equivalent:** Project paths in the CLI are established per-command using the `-p` flag, e.g. `scrivener-cli -p /Users/me/Documents/MyNovel.scriv <command>`)*

---

## Step 2: Explore Binder

Understand what is in your project to find the right documents to work on.

**User Prompt:**
> "Show me the binder structure of my project."

**MCP Tool Called:** `get_binder_structure`

**CLI Command:**
`scrivener-cli -p /Users/me/Documents/MyNovel.scriv binder`

**AI Response (Example):**
> *   **Draft** (UUID: `4A1D...`)
>     *   **Chapter 1** (UUID: `FD75...`)
>         *   *Scene 1: The Inciting Incident* (UUID: `0A7E...`)

---

## Step 3: Read Content

Read the actual text of a scene to understand the context.

**User Prompt:**
> "Read the content of 'Scene 1' (UUID: 0A7E...)."

**MCP Tool Called:** `read_document(uuid="0A7E...")`

**CLI Command:**
`scrivener-cli -p /Users/me/Documents/MyNovel.scriv read "0A7E..."`

---

## Step 4: Create Reusable Prompts

Instead of typing out long analysis instructions every time, save them as a reusable prompt in your configured `<storage_path>` library (defaults to `.ai-assistant`).

**User Prompt:**
> "Save a prompt called 'scene_analysis'. The content should be: 'Analyze this scene for pacing...'"

**MCP Tool Called:** `save_prompt(name="scene_analysis", content="...")`

**CLI Command:**
`scrivener-cli -p /Users/me/Documents/MyNovel.scriv prompt save "scene_analysis" "Analyze this scene..."`

---

## Step 5: Analyze & Update Metadata

Now, combine everything. Read a chapter, use your saved prompt to analyze it, and store the result back into Scrivener's custom metadata so you can see it in the Inspector or Outliner.

**User Prompt:**
> "Please analyze 'Scene 1' using the 'scene_analysis' prompt. Then, update the scene's metadata: set 'Status' to 'Reviewed' and create a new field 'AnalysisSummary' with a one-sentence summary of your feedback."

**MCP Tools Called:**
1.  `get_prompt(name="scene_analysis")` -> Retrieves your analysis instructions.
2.  `read_document(uuid="...")` -> Reads the scene text.
3.  *(AI performs analysis internally)*
4.  `update_metadata(uuid="...", field="Status", value="Reviewed")`
5.  `update_metadata(uuid="...", field="AnalysisSummary", value="Strong pacing, but dialogue needs work.")`

**CLI Commands:**
```bash
scrivener-cli -p /path/to.scriv prompt get "scene_analysis"
scrivener-cli -p /path/to.scriv read "UUID"
# ... AI computes offline ...
scrivener-cli -p /path/to.scriv metadata update "UUID" "Status" "Reviewed"
scrivener-cli -p /path/to.scriv metadata update "UUID" "AnalysisSummary" "Strong pacing..."
```

---

## Advanced: Full Project Context

You can also ask broad questions if the AI has read enough context.

**User Prompt:**
> "Based on the 'AnalysisSummary' metadata of all scenes in Chapter 1, does the pacing lag in the middle?"

*(Note: The AI might need to loop through documents to read their metadata first, or you can ask it to "Check the metadata for all children of Chapter 1".)*

---

## Efficient Batch Analysis

Instead of reading a chapter multiple times for different analyses, use the batch analysis workflow to save time and tokens.

**User Prompt:**
> "Use batch analysis on Scene 1 to generate a summary, extract metadata, and provide a style review."

**What Happens Behind the Scenes:**
1. AI calls `prepare_chapter_analysis(uuid)` - reads chapter **once**
2. AI receives full chapter content + workflow instructions
3. AI performs all three analyses in sequence:
   - Generates summary → calls `save_summary(uuid, summary_text)`
   - Extracts metadata → calls `update_metadata(uuid, field, value)` multiple times
   - Writes style review → calls `save_review(uuid, review_text)`

**Result:** All three outputs stored in your selected storage folder:
- `<storage_path>/summaries/[uuid].md`
- `<storage_path>/reviews/[uuid].md`
- Custom metadata fields updated in `.scrivx`

**Token Savings:** ~66% (1 read instead of 3 separate reads)

---

## Style Review Workflow

Get detailed editorial feedback on your writing style.

**User Prompt:**
> "Analyze the writing style of Chapter 2 and save a review with strengths, weaknesses, and improvement suggestions."

**AI Response Example:**
> "I've analyzed Chapter 2 and saved a comprehensive style review. Here's what I found:
>
> **Strengths:**
> - Strong character voice in dialogue
> - Effective use of sensory details
> - Good pacing in action scenes
>
> **Weaknesses:**
> - Overuse of adverbs (8 instances of 'quickly', 'slowly')
> - Some telling instead of showing in emotional moments
> - Repetitive sentence structure in paragraphs 3-5
>
> **Suggestions:**
> - Replace 'walked slowly' with 'shuffled' or 'trudged'
> - Show the character's nervousness through physical actions instead of stating 'she felt nervous'
> - Vary sentence length for better rhythm
>
> The full review has been saved to `<storage_path>/reviews/[chapter-uuid].md`"

**Retrieve Later:**
retrieves
> "Show me the style review for Chapter 2"

AI calls `get_review(uuid)` and displays the saved feedback.

