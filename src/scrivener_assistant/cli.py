"""
Scrivener Assistant CLI
Command-line interface for interacting with Scrivener projects.
"""
import sys
import json
import argparse
from typing import Optional
from scrivener_assistant import ScrivenerProject

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scrivener Assistant CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-p", "--project",
        dest="project_path",
        required=True,
        help="Path to the .scriv project directory"
    )

    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # Command: binder
    subparsers.add_parser("binder", help="Get the binder structure")

    # Command: read
    read_parser = subparsers.add_parser("read", help="Read a document by UUID")
    read_parser.add_argument("uuid", help="The UUID of the document")

    # Command: metadata
    metadata_parser = subparsers.add_parser("metadata", help="Metadata tools")
    metadata_subparsers = metadata_parser.add_subparsers(dest="subcommand", required=True)
    md_update_parser = metadata_subparsers.add_parser("update", help="Update metadata")
    md_update_parser.add_argument("uuid", help="The UUID of the document")
    md_update_parser.add_argument("field", help="The name of the metadata field")
    md_update_parser.add_argument("value", help="The value to set")

    # Command: prompt
    prompt_parser = subparsers.add_parser("prompt", help="Prompt tools")
    prompt_subparsers = prompt_parser.add_subparsers(dest="subcommand", required=True)
    prompt_subparsers.add_parser("list", help="List available prompts")
    p_get_parser = prompt_subparsers.add_parser("get", help="Get a prompt")
    p_get_parser.add_argument("name", help="Name of the prompt")
    p_save_parser = prompt_subparsers.add_parser("save", help="Save a prompt")
    p_save_parser.add_argument("name", help="Name of the prompt")
    p_save_parser.add_argument("content", help="Prompt content")

    # Command: summary
    summary_parser = subparsers.add_parser("summary", help="Summary tools")
    summary_subparsers = summary_parser.add_subparsers(dest="subcommand", required=True)
    s_get_parser = summary_subparsers.add_parser("get", help="Get a summary")
    s_get_parser.add_argument("uuid", help="The UUID of the document")
    s_save_parser = summary_subparsers.add_parser("save", help="Save a summary")
    s_save_parser.add_argument("uuid", help="The UUID of the document")
    s_save_parser.add_argument("content", help="Summary content")

    # Command: review
    review_parser = subparsers.add_parser("review", help="Review tools")
    review_subparsers = review_parser.add_subparsers(dest="subcommand", required=True)
    r_get_parser = review_subparsers.add_parser("get", help="Get a review")
    r_get_parser.add_argument("uuid", help="The UUID of the document")
    r_save_parser = review_subparsers.add_parser("save", help="Save a review")
    r_save_parser.add_argument("uuid", help="The UUID of the document")
    r_save_parser.add_argument("content", help="Review content")
    r_history_parser = review_subparsers.add_parser("history", help="Get review history")
    r_history_parser.add_argument("uuid", help="The UUID of the document")
    r_prev_parser = review_subparsers.add_parser("previous", help="Get previous review")
    r_prev_parser.add_argument("uuid", help="The UUID of the document")
    r_arch_parser = review_subparsers.add_parser("archived", help="Get an archived review by timestamp")
    r_arch_parser.add_argument("uuid", help="The UUID of the document")
    r_arch_parser.add_argument("timestamp", help="The timestamp string")

    # Command: chapter
    chapter_parser = subparsers.add_parser("chapter", help="Chapter tools")
    chapter_subparsers = chapter_parser.add_subparsers(dest="subcommand", required=True)
    c_prep_parser = chapter_subparsers.add_parser("prepare", help="Prepare chapter analysis")
    c_prep_parser.add_argument("uuid", help="The UUID of the document")

    # Command: character
    char_parser = subparsers.add_parser("character", help="Character tools")
    char_subparsers = char_parser.add_subparsers(dest="subcommand", required=True)
    char_subparsers.add_parser("list", help="List characters")
    ch_get_parser = char_subparsers.add_parser("get", help="Get a character")
    ch_get_parser.add_argument("name", help="Character name")
    ch_save_parser = char_subparsers.add_parser("save", help="Save a character")
    ch_save_parser.add_argument("name", help="Character name")
    ch_save_parser.add_argument("content", help="Character content")

    # Command: location
    loc_parser = subparsers.add_parser("location", help="Location tools")
    loc_subparsers = loc_parser.add_subparsers(dest="subcommand", required=True)
    loc_subparsers.add_parser("list", help="List locations")
    l_get_parser = loc_subparsers.add_parser("get", help="Get a location")
    l_get_parser.add_argument("name", help="Location name")
    l_save_parser = loc_subparsers.add_parser("save", help="Save a location")
    l_save_parser.add_argument("name", help="Location name")
    l_save_parser.add_argument("content", help="Location content")

    return parser


def handle_metadata(args, project: ScrivenerProject):
    if args.subcommand == "update":
        project.update_metadata(args.uuid, args.field, args.value)
        print(f"Successfully updated metadata '{args.field}' for {args.uuid}")

def handle_prompt(args, project: ScrivenerProject):
    if args.subcommand == "list":
        prompts = project.list_prompts()
        if not prompts:
            print("No prompts found.")
        else:
            print("Available prompts:\n" + "\n".join(f"- {p}" for p in prompts))
    elif args.subcommand == "get":
        prompt = project.get_prompt(args.name)
        if prompt:
            print(prompt)
        else:
            print(f"Prompt '{args.name}' not found.")
    elif args.subcommand == "save":
        path = project.save_prompt(args.name, args.content)
        print(f"Saved prompt '{args.name}' to {path}")


def handle_summary(args, project: ScrivenerProject):
    if args.subcommand == "get":
        summary = project.get_summary(args.uuid)
        if summary:
            print(summary)
        else:
            print(f"Summary for {args.uuid} not found.")
    elif args.subcommand == "save":
        path = project.save_summary(args.uuid, args.content)
        print(f"Saved summary for {args.uuid} at {path}")

def handle_review(args, project: ScrivenerProject):
    if args.subcommand == "get":
        review = project.get_review(args.uuid)
        if review:
            print(review)
        else:
            print(f"Style review for {args.uuid} not found.")
    elif args.subcommand == "save":
        path = project.save_review(args.uuid, args.content)
        print(f"Saved style review for {args.uuid} at {path}")
    elif args.subcommand == "history":
        history = project.review_manager.get_review_history(args.uuid)
        print(json.dumps(history, indent=2))
    elif args.subcommand == "previous":
        history = project.review_manager.get_review_history(args.uuid)
        if not history:
            print("No previous reviews found.")
        else:
            last_review = history[0]
            content = project.review_manager.get_archived_review(args.uuid, last_review["timestamp"])
            if content:
                print(f"# Previous Review ({last_review['timestamp']})\n\n{content}")
            else:
                print(f"Error reading archived review {last_review['timestamp']}")
    elif args.subcommand == "archived":
        content = project.review_manager.get_archived_review(args.uuid, args.timestamp)
        if content:
            print(content)
        else:
            print(f"Archived review for {args.uuid} at {args.timestamp} not found.")

def handle_chapter(args, project: ScrivenerProject):
    if args.subcommand == "prepare":
        content = project.read_document(args.uuid)
        if not content or content.startswith("[Error"):
            print(f"Error: Could not read document {args.uuid}")
            return
        
        output = f"""# CHAPTER ANALYSIS PREPARED

## Document UUID
{args.uuid}

## Chapter Content
{content}

---

## ANALYSIS WORKFLOW
Now that you have the chapter content, perform the following analyses:

### 1. Generate Summary
- Create a concise summary (2-3 paragraphs)
- Call: `scrivener-cli -p "{args.project_path}" summary save "{args.uuid}" "<your_summary>"`

### 2. Extract Metadata
- Identify key metadata (status, setting, POV character, etc.)
- Call: `scrivener-cli -p "{args.project_path}" metadata update "{args.uuid}" "<field_name>" "<value>"` for each field

### 3. Write Style Review
- Analyze: strengths, weaknesses, style suggestions
- Format as markdown with sections
- Call: `scrivener-cli -p "{args.project_path}" review save "{args.uuid}" "<your_review>"`

All three tasks can be completed efficiently since the chapter has been read once.
"""
        print(output)


def handle_character(args, project: ScrivenerProject):
    if args.subcommand == "list":
        chars = project.list_characters()
        if not chars:
            print("No characters found.")
        else:
            print("Available characters:\n" + "\n".join(f"- {c}" for c in chars))
    elif args.subcommand == "get":
        content = project.get_character(args.name)
        if content:
            print(content)
        else:
            print(f"Character '{args.name}' not found.")
    elif args.subcommand == "save":
        path = project.save_character(args.name, args.content)
        print(f"Saved character '{args.name}' into {path}")

def handle_location(args, project: ScrivenerProject):
    if args.subcommand == "list":
        locs = project.list_locations()
        if not locs:
            print("No locations found.")
        else:
            print("Available locations:\n" + "\n".join(f"- {l}" for l in locs))
    elif args.subcommand == "get":
        content = project.get_location(args.name)
        if content:
            print(content)
        else:
            print(f"Location '{args.name}' not found.")
    elif args.subcommand == "save":
        path = project.save_location(args.name, args.content)
        print(f"Saved location '{args.name}' into {path}")


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        project = ScrivenerProject(args.project_path)
    except Exception as e:
        print(f"Error loading project: {e}", file=sys.stderr)
        sys.exit(1)

    # Dispatch logic
    if args.command == "binder":
        print(json.dumps(project.get_structure(), indent=2))
    elif args.command == "read":
        print(project.read_document(args.uuid))
    elif args.command == "metadata":
        handle_metadata(args, project)
    elif args.command == "prompt":
        handle_prompt(args, project)
    elif args.command == "summary":
        handle_summary(args, project)
    elif args.command == "review":
        handle_review(args, project)
    elif args.command == "chapter":
        handle_chapter(args, project)
    elif args.command == "character":
        handle_character(args, project)
    elif args.command == "location":
        handle_location(args, project)

if __name__ == "__main__":
    main()
