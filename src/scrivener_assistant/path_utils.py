import re
from pathlib import Path

def slugify(text: str) -> str:
    """
    Converts a string into a filesystem-friendly slug.
    Example: "Chapter 1: The Beginning" -> "chapter-1-the-beginning"
    """
    # Remove non-word characters (except spaces and hyphens), then replace spaces with hyphens
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[-\s]+', '-', text).strip('-')
    return text[:64]  # Truncate to reasonable length

def generate_hybrid_filename(title: str, uuid: str) -> str:
    """
    Generates a filename in the format {slug}--{short-uuid}.md
    """
    slug = slugify(title)
    short_uuid = uuid.split('-')[0]  # Take first part of UUID (usually 8 chars)
    
    if not slug:
        return f"untitled--{short_uuid}.md"
    
    return f"{slug}--{short_uuid}.md"

def get_short_uuid(uuid: str) -> str:
    """Returns the short version (first group) of a UUID."""
    return uuid.split('-')[0]
