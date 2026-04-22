"""
Scrivener Assistant MCP Server
Entry point for the Model Context Protocol server.
"""
import os
import sys
import logging
import argparse
from typing import Optional
from mcp.server.fastmcp import FastMCP
from scrivener_assistant import ScrivenerProject

# Initialize FastMCP Server
mcp = FastMCP("Scrivener assistant")

# Global state to hold the current project
current_project: Optional[ScrivenerProject] = None

NO_PROJECT_MSG = "No project loaded. Please use the `set_project_path` tool to load a valid .scriv project first."

@mcp.tool()
def set_project_path(path: str) -> str:
    """
    Sets the active Scrivener project.
    
    Args:
        path: Absolute path to the .scriv directory.
    
    Returns:
        Status message confirming the project loaded or error.
    """
    global current_project
    try:
        project = ScrivenerProject(path)
        current_project = project
        return f"Successfully loaded project: {project.path}"
    except Exception as e:
        return f"Error loading project: {str(e)}"

@mcp.tool()
def get_current_project() -> str:
    """Returns the path of the currently loaded project."""
    if current_project:
        return str(current_project.path)
    return NO_PROJECT_MSG

@mcp.tool()
def get_binder_structure() -> str:
    """
    Returns the binder structure of the current project as a JSON string.
    """
    if not current_project:
        return NO_PROJECT_MSG
    
    import json
    try:
        structure = current_project.get_structure()
        return json.dumps(structure, indent=2)
    except Exception as e:
        return f"Error parsing binder: {str(e)}"

@mcp.tool()
def read_document(uuid: str) -> str:
    """
    Reads the content of a document by UUID.
    
    Args:
        uuid: The UUID of the document to read.
        
    Returns:
        The text content of the document, or error message.
    """
    if not current_project:
        return NO_PROJECT_MSG
    
    return current_project.read_document(uuid)

@mcp.tool()
def read_document_notes(uuid: str) -> str:
    """
    Reads the inspector notes of a document by UUID.

    In Scrivener, the Notes panel (Inspector) is used to store research,
    reminders, or annotations alongside a document without appearing in
    the compiled manuscript.

    Args:
        uuid: The UUID of the document whose notes to read.

    Returns:
        The plain text content of the notes, or empty string if none exist.
    """
    if not current_project:
        return NO_PROJECT_MSG

    return current_project.read_notes(uuid)

@mcp.tool()
def read_document_synopsis(uuid: str) -> str:
    """
    Reads the synopsis of a document by UUID.

    In Scrivener, the synopsis is a short summary visible on index cards
    in the corkboard and outliner views. It is stored as plain text.

    Args:
        uuid: The UUID of the document whose synopsis to read.

    Returns:
        The plain text synopsis, or empty string if none exists.
    """
    if not current_project:
        return NO_PROJECT_MSG

    return current_project.read_synopsis(uuid)

@mcp.tool()
def update_metadata(uuid: str, field: str, value: str) -> str:
    """
    Updates the custom metadata for a document.
    
    Args:
        uuid: The UUID of the document.
        field: The name of the metadata field (e.g. "Status", "Philosophy").
        value: The value to set.
        
    Returns:
        Status message.
    """
    print(f"[DEBUG] update_metadata called: uuid={uuid}, field={field}, value={value}", file=sys.stderr)
    
    if not current_project:
        return NO_PROJECT_MSG
        
    try:
        print(f"[DEBUG] Calling current_project.update_metadata", file=sys.stderr)
        current_project.update_metadata(uuid, field, value)
        print(f"[DEBUG] update_metadata succeeded", file=sys.stderr)
        return f"Successfully updated metadata '{field}' for {uuid}."
    except Exception as e:
        print(f"[DEBUG] update_metadata FAILED: {e}", file=sys.stderr)
        return f"Error updating metadata: {str(e)}"

@mcp.tool()
def save_prompt(name: str, content: str) -> str:
    """
    Saves a reusable prompt to the project's library.
    
    Args:
        name: The name of the prompt (e.g., "analyze_chapter").
        content: The prompt text.
    """
    if not current_project:
        return NO_PROJECT_MSG
    try:
        path = current_project.save_prompt(name, content)
        return f"Saved prompt '{name}' to {path}"
    except Exception as e:
        return f"Error saving prompt: {e}"

@mcp.tool()
def get_prompt(name: str) -> str:
    """
    Retrieves a reusable prompt.
    """
    if not current_project:
        return NO_PROJECT_MSG
    prompt = current_project.get_prompt(name)
    if prompt:
        return prompt
    return f"Prompt '{name}' not found."

@mcp.tool()
def list_prompts() -> str:
    """
    Lists available reusable prompts.
    """
    if not current_project:
        return NO_PROJECT_MSG
    prompts = current_project.list_prompts()
    if not prompts:
        return "No prompts found."
    return "Available prompts:\n" + "\n".join(f"- {p}" for p in prompts)
    
@mcp.tool()
def save_summary(uuid: str, content: str) -> str:
    """
    Saves a summary for a specific document (chapter/scene).
    
    Args:
        uuid: The UUID of the document.
        content: The summary text.
    """
    if not current_project:
        return NO_PROJECT_MSG
    try:
        path = current_project.save_summary(uuid, content)
        return f"Saved summary for {uuid} at {path}"
    except Exception as e:
        return f"Error saving summary: {e}"

@mcp.tool()
def get_summary(uuid: str) -> str:
    """
    Retrieves the cached summary for a document.
    """
    if not current_project:
        return NO_PROJECT_MSG
    summary = current_project.get_summary(uuid)
    if summary:
        return summary
    return f"Summary for {uuid} not found."

@mcp.tool()
def save_review(uuid: str, content: str) -> str:
    """
    Saves a style review for a specific document (chapter/scene).
    
    Args:
        uuid: The UUID of the document.
        content: The style review text (strengths, weaknesses, suggestions).
    """
    print(f"[DEBUG] save_review called: uuid={uuid}", file=sys.stderr)
    if not current_project:
        return NO_PROJECT_MSG
    try:
        print(f"[DEBUG] Calling current_project.save_review", file=sys.stderr)
        path = current_project.save_review(uuid, content)
        return f"Saved style review for {uuid} at {path}"
    except Exception as e:
        print(f"[DEBUG] save_review failed: {e}", file=sys.stderr)
        return f"Error saving review: {e}"

@mcp.tool()
def get_review(uuid: str) -> str:
    """
    Retrieves the cached style review for a document.
    """
    if not current_project:
        return NO_PROJECT_MSG
    review = current_project.get_review(uuid)
    if review:
        return review
    return f"Style review for {uuid} not found."

@mcp.tool()
def get_review_history(uuid: str) -> str:
    """
    Retrieves the history of past reviews for a document.
    Returns a JSON string of a list of dicts: [{"timestamp": "...", "path": "..."}]
    ordered by most recent first.
    """
    if not current_project:
        return NO_PROJECT_MSG
    
    import json
    history = current_project.review_manager.get_review_history(uuid)
    return json.dumps(history, indent=2)

@mcp.tool()
def get_previous_review(uuid: str) -> str:
    """
    Retrieves the content of the MOST RECENT archived review.
    Useful for comparing the current state against the immediate past feedback.
    """
    if not current_project:
        return NO_PROJECT_MSG
    
    history = current_project.review_manager.get_review_history(uuid)
    if not history:
        return "No previous reviews found."
    
    # Get the most recent one (history is sorted reverse)
    last_review = history[0]
    timestamp = last_review["timestamp"]
    
    content = current_project.review_manager.get_archived_review(uuid, timestamp)
    if content:
        return f"# Previous Review ({timestamp})\n\n{content}"
    return f"Error reading archived review {timestamp}"

@mcp.tool()
def get_archived_review(uuid: str, timestamp: str) -> str:
    """
    Retrieves the content of a specific archived review by timestamp.
    Timestamp format should match what is returned by `get_review_history`.
    """
    if not current_project:
        return NO_PROJECT_MSG
    
    content = current_project.review_manager.get_archived_review(uuid, timestamp)
    if content:
        return content
    return f"Archived review for {uuid} at {timestamp} not found."

@mcp.tool()
def prepare_chapter_analysis(uuid: str) -> str:
    """
    Prepares a chapter for comprehensive batch analysis.
    Returns the chapter content along with suggested analysis workflow.
    This allows AI to read the chapter once and perform multiple tasks:
    summary, metadata extraction, and style review.
    
    Args:
        uuid: The UUID of the document/chapter to analyze.
    
    Returns:
        Chapter content with analysis workflow instructions.
    """
    if not current_project:
        return NO_PROJECT_MSG
    
    try:
        # Read chapter content ONCE
        content = current_project.read_document(uuid)
        
        if not content or content.startswith("[Error"):
            return f"Error: Could not read document {uuid}"
        
        # Return structured workflow
        return f"""# CHAPTER ANALYSIS PREPARED

## Document UUID
{uuid}

## Chapter Content
{content}

---

## ANALYSIS WORKFLOW
Now that you have the chapter content, perform the following analyses:

### 1. Generate Summary
- Create a concise summary (2-3 paragraphs)
- Call: `save_summary("{uuid}", <your_summary>)`

### 2. Extract Metadata
- Identify key metadata (status, setting, POV character, etc.)
- Call: `update_metadata("{uuid}", "<field_name>", "<value>")` for each field

### 3. Write Style Review
- Analyze: strengths, weaknesses, style suggestions
- Format as markdown with sections
- Call: `save_review("{uuid}", <your_review>)`

All three tasks can be completed efficiently since the chapter has been read once.
"""
    except Exception as e:
        logger.error(f"Error preparing chapter analysis for {uuid}: {e}")
        return f"Error preparing analysis: {e}"

        return f"Error preparing analysis: {e}"

# --- Character Tools ---

@mcp.tool()
def save_character(name: str, content: str) -> str:
    """
    Saves a character profile.
    
    Args:
        name: Name of the character (e.g., "Gandalf").
        content: The character profile content.
    """
    if not current_project:
        return NO_PROJECT_MSG
    try:
        path = current_project.save_character(name, content)
        return f"Saved character '{name}' into {path}"
    except Exception as e:
        return f"Error saving character: {e}"

@mcp.tool()
def get_character(name: str) -> str:
    """ Retrieves a character profile. """
    if not current_project:
        return NO_PROJECT_MSG
    content = current_project.get_character(name)
    if content:
        return content
    return f"Character '{name}' not found."

@mcp.tool()
def list_characters() -> str:
    """ Lists available character profiles. """
    if not current_project:
        return NO_PROJECT_MSG
    chars = current_project.list_characters()
    if not chars:
        return "No characters found."
    return "Available characters:\n" + "\n".join(f"- {c}" for c in chars)

# --- Location Tools ---

@mcp.tool()
def save_location(name: str, content: str) -> str:
    """
    Saves a location profile.
    
    Args:
        name: Name of the location (e.g., "Rivendell").
        content: The location profile content.
    """
    if not current_project:
        return NO_PROJECT_MSG
    try:
        path = current_project.save_location(name, content)
        return f"Saved location '{name}' into {path}"
    except Exception as e:
        return f"Error saving location: {e}"

@mcp.tool()
def get_location(name: str) -> str:
    """ Retrieves a location profile. """
    if not current_project:
        return NO_PROJECT_MSG
    content = current_project.get_location(name)
    if content:
        return content
    return f"Location '{name}' not found."

@mcp.tool()
def list_locations() -> str:
    """ Lists available location profiles. """
    if not current_project:
        return NO_PROJECT_MSG
    locs = current_project.list_locations()
    if not locs:
        return "No locations found."
    return "Available locations:\n" + "\n".join(f"- {l}" for l in locs)

# --- World Tools ---

@mcp.tool()
def get_world(section: str = "") -> str:
    """
    Reads world context from world/.
    Args:
        section: One of style, bible, structure, plan, timeline, synthesis.
                 Leave empty to get all sections concatenated.
    """
    if not current_project:
        return NO_PROJECT_MSG
    try:
        data = current_project.get_world(section)
        if not data:
            return f"No world data found{' for section ' + section if section else ''}."
        if section:
            return data.get(section, f"Section '{section}' not found.")
        return "\n\n---\n\n".join(f"# {k}\n\n{v}" for k, v in sorted(data.items()))
    except Exception as e:
        return f"Error reading world: {e}"

@mcp.tool()
def save_world(section: str, content: str) -> str:
    """
    Writes a world context file.
    Args:
        section: One of style, bible, structure, plan, timeline, synthesis.
        content: Full markdown content to write.
    """
    if not current_project:
        return NO_PROJECT_MSG
    try:
        path = current_project.save_world(section, content)
        return f"Saved world section '{section}' to {path}"
    except ValueError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error saving world section: {e}"

# --- State Tools ---

@mcp.tool()
def get_story_state(chapter: int = 0) -> str:
    """
    Reads story state.
    Args:
        chapter: Chapter number to read archived state for.
                 Pass 0 (default) to read current state.
    Returns all 4 state files (situation, characters, knowledge, inventory).
    """
    if not current_project:
        return NO_PROJECT_MSG
    try:
        state = current_project.get_story_state(chapter)
        if not state:
            label = "current state" if chapter == 0 else f"state for chapter {chapter:02d}"
            return f"No {label} found. Run the bootstrap or save_story_state to initialize."
        label = "Current state" if chapter == 0 else f"State — chapter {chapter:02d}"
        parts = [f"# {label}"]
        for key in ["situation", "characters", "knowledge", "inventory"]:
            parts.append(f"\n## {key.capitalize()}\n\n{state.get(key, '')}")
        return "\n".join(parts)
    except Exception as e:
        return f"Error reading story state: {e}"

@mcp.tool()
def save_story_state(chapter: int, situation: str, characters: str, knowledge: str, inventory: str) -> str:
    """
    Saves a chapter state snapshot and updates state/current/.
    Archives the previous current state under state/chapter-NN/ first.
    Args:
        chapter: The chapter number just completed (used for archiving).
        situation: Open story hooks, immediate context.
        characters: Emotional/positional state of each character.
        knowledge: What each character knows at this point.
        inventory: Object locations and ownership.
    """
    if not current_project:
        return NO_PROJECT_MSG
    try:
        path = current_project.save_story_state(chapter, situation, characters, knowledge, inventory)
        return f"Saved state for chapter {chapter:02d}. Current state updated at {path}"
    except Exception as e:
        return f"Error saving story state: {e}"

@mcp.tool()
def list_story_states() -> str:
    """Lists all archived chapter state snapshots."""
    if not current_project:
        return NO_PROJECT_MSG
    snapshots = current_project.list_story_states()
    if not snapshots:
        return "No archived state snapshots found."
    return "Archived state snapshots:\n" + "\n".join(f"- {s}" for s in snapshots)

# --- Draft Tools ---

@mcp.tool()
def save_brainstorm(chapter: int, content: str) -> str:
    """
    Saves brainstorm notes for a chapter.
    Args:
        chapter: Chapter number.
        content: Notes from the brainstorm session.
    """
    if not current_project:
        return NO_PROJECT_MSG
    try:
        path = current_project.save_brainstorm(chapter, content)
        return f"Saved brainstorm for chapter {chapter:02d} to {path}"
    except Exception as e:
        return f"Error saving brainstorm: {e}"

@mcp.tool()
def save_beats(chapter: int, content: str) -> str:
    """
    Saves scene beats for a chapter.
    Args:
        chapter: Chapter number.
        content: Scene-by-scene plan (5–8 beats).
    """
    if not current_project:
        return NO_PROJECT_MSG
    try:
        path = current_project.save_beats(chapter, content)
        return f"Saved beats for chapter {chapter:02d} to {path}"
    except Exception as e:
        return f"Error saving beats: {e}"

@mcp.tool()
def save_draft(chapter: int, content: str) -> str:
    """
    Saves AI-generated prose for a chapter.
    Args:
        chapter: Chapter number.
        content: Full prose draft.
    """
    if not current_project:
        return NO_PROJECT_MSG
    try:
        path = current_project.save_draft(chapter, content)
        return f"Saved draft for chapter {chapter:02d} to {path}"
    except Exception as e:
        return f"Error saving draft: {e}"

@mcp.tool()
def get_draft(chapter: int) -> str:
    """
    Reads the AI draft for a chapter.
    Args:
        chapter: Chapter number.
    """
    if not current_project:
        return NO_PROJECT_MSG
    content = current_project.get_draft(chapter)
    if content:
        return content
    return f"No draft found for chapter {chapter:02d}."

# --- Extraction Tool ---

@mcp.tool()
def extract_bible_from_chapters(uuids: list) -> str:
    """
    Reads a list of Scrivener documents and returns aggregated text ready
    for bible extraction. Does NOT save anything — returns the content so
    Claude can analyze it and the user can confirm before saving to world/.

    Args:
        uuids: List of document UUIDs to read and aggregate.
    """
    if not current_project:
        return NO_PROJECT_MSG
    if not uuids:
        return "Error: provide at least one UUID."

    parts = []
    errors = []
    for uuid in uuids:
        content = current_project.read_document(uuid)
        if not content:
            errors.append(uuid)
            continue
        node = current_project.binder_map.get(uuid)
        title = node.title if node else uuid
        parts.append(f"## {title} ({uuid})\n\n{content}")

    if errors:
        error_note = f"\n\n> Could not read {len(errors)} document(s): {', '.join(errors)}"
    else:
        error_note = ""

    aggregated = "\n\n---\n\n".join(parts) + error_note

    return f"""# Chapters for Bible Extraction

{aggregated}

---

## Analysis Instructions

Based on the chapters above, extract the following and return structured markdown:

### 1. Style guide (for world/style.md)
- Narrative POV and tense
- Sentence rhythm patterns (with examples)
- Vocabulary register and recurring phrases
- Distinctive stylistic techniques

### 2. Characters (for world/characters/<name>.md per character)
- Name, approximate age, role
- Personality traits and speech patterns
- Key relationships
- Knowledge state at end of last chapter

### 3. Locations (for world/locations/<name>.md per location)
- Name and physical description
- Atmosphere and sensory details
- Story function

### 4. Narrative structure (for world/structure.md)
- Main themes
- Story arc so far
- Open plot threads

After analysis, save each section using save_world(), save_character(), save_location() as appropriate.
"""


def main():
    global current_project
    
    # Parse CLI args
    parser = argparse.ArgumentParser(
        description="Scrivener Assistant MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python server.py -p /path/to/project.scriv
  python server.py -p /path/to/project.scriv -v
  python server.py --verbose --project /path/to/project.scriv
        """
    )
    parser.add_argument(
        "-p", "--project",
        dest="project_path",
        metavar="PATH",
        help="Path to the .scriv project directory"
    )
    parser.add_argument(
        "-s", "--storage",
        dest="storage_path",
        metavar="PATH",
        help="Path to store assistant files (overrides SCRIVENER_ASSISTANT_FOLDER)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable debug logging (default: INFO level)"
    )
    
    args = parser.parse_args()

    # Fall back to env var injected by the Desktop Extension manifest
    if not args.project_path:
        env_path = os.environ.get("SCRIVENER_PROJECT_PATH", "").strip().strip("'\"")
        if env_path:
            args.project_path = env_path
            
    if args.storage_path:
        os.environ["SCRIVENER_ASSISTANT_FOLDER"] = args.storage_path

    # Configure logging based on verbosity
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
        logging.FileHandler('/tmp/scrivener_mcp_debug.log'), 
        logging.StreamHandler()
    ]
    )
    logger = logging.getLogger("scrivener_mcp")
    
    logger.info(f"Starting Scrivener Assistant MCP Server (log level: {logging.getLevelName(log_level)})")

    # Load initial project if provided
    if args.project_path:
        try:
            logger.info(f"Loading initial project: {args.project_path}")
            current_project = ScrivenerProject(args.project_path)
            logger.info(f"Successfully loaded project: {current_project.path}")
        except Exception as e:
            logger.error(f"Failed to load initial project: {e}")
            sys.exit(1)
    else:
        logger.info("No initial project specified. Use set_project_path tool to load a project.")

    # Clean sys.argv so FastMCP doesn't try to parse our arguments
    sys.argv = [sys.argv[0]]

    # Start the server
    logger.info("Starting MCP server...")
    mcp.run()

if __name__ == "__main__":
    main()

