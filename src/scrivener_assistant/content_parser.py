from pathlib import Path
from typing import Optional

def get_content_path(project_path: Path, uuid: str) -> Optional[Path]:
    """
    Locates the content.rtf file for a given UUID within the project.

    Args:
        project_path: Absolute path to the .scriv directory.
        uuid: The UUID of the binder item.

    Returns:
        Path to the content.rtf file if it exists, else None.
    """
    # Scrivener 3 structure: Files/Data/{UUID}/content.rtf
    possible_path = project_path / "Files" / "Data" / uuid / "content.rtf"

    if possible_path.exists():
        return possible_path

    return None


def get_notes_path(project_path: Path, uuid: str) -> Optional[Path]:
    """
    Locates the notes.rtf file for a given UUID within the project.

    Args:
        project_path: Absolute path to the .scriv directory.
        uuid: The UUID of the binder item.

    Returns:
        Path to the notes.rtf file if it exists, else None.
    """
    possible_path = project_path / "Files" / "Data" / uuid / "notes.rtf"

    if possible_path.exists():
        return possible_path

    return None


def get_synopsis_path(project_path: Path, uuid: str) -> Optional[Path]:
    """
    Locates the synopsis.txt file for a given UUID within the project.

    Args:
        project_path: Absolute path to the .scriv directory.
        uuid: The UUID of the binder item.

    Returns:
        Path to the synopsis.txt file if it exists, else None.
    """
    possible_path = project_path / "Files" / "Data" / uuid / "synopsis.txt"

    if possible_path.exists():
        return possible_path

    return None
