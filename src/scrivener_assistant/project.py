from pathlib import Path
from typing import Optional, Dict, List
import logging
from scrivener_assistant.base_manager import BaseSceneDataManager
from scrivener_assistant.binder_parser import parse_scrivx, get_binder_map
from scrivener_assistant.content_parser import get_content_path
from scrivener_assistant.rtf_converter import convert_rtf_to_text
from scrivener_assistant.metadata_manager import MetadataManager
from scrivener_assistant.prompt_manager import PromptManager
from scrivener_assistant.summary_manager import SummaryManager
from scrivener_assistant.review_manager import ReviewManager
from scrivener_assistant.config import ProjectConfig

logger = logging.getLogger(__name__)

class ScrivenerProject:
    """
    Represents a Scrivener project directory.
    """
    def __init__(self, project_path: str, config: Optional[ProjectConfig] = None):
        logger.debug(f"Initializing ScrivenerProject for path: {project_path}")
        
        self.path = Path(project_path).resolve()
        self.config = config or ProjectConfig.default()
        self._validate_path()
        
        # 1. Parse binder first
        logger.debug("Parsing binder structure")
        self.nodes = parse_scrivx(self.scrivx_file)
        self.binder_map = get_binder_map(self.nodes)
        
        # 2. Inject config and binder map into managers
        logger.debug("Initializing managers")
        self.metadata_manager = MetadataManager(self.scrivx_file, self.config)
        self.prompt_manager = PromptManager(self.path, self.config)
        self.summary_manager = SummaryManager(self.path, self.config, binder_map=self.binder_map)
        self.review_manager = ReviewManager(self.path, self.config, binder_map=self.binder_map)
        self.character_manager = BaseSceneDataManager(self.path, self.config.characters_subfolder, self.config, binder_map=None)
        self.location_manager = BaseSceneDataManager(self.path, self.config.locations_subfolder, self.config, binder_map=None)
        
        logger.info(f"ScrivenerProject initialized successfully for {self.path}")

    def _validate_path(self) -> None:
        """
        Validates that the path exists and is a valid .scriv directory.
        """
        logger.debug(f"Validating project path: {self.path}")
        
        if not self.path.exists():
            logger.error(f"Project path does not exist: {self.path}")
            raise FileNotFoundError(f"Project path does not exist: {self.path}")
        
        if not self.path.is_dir():
            logger.error(f"Project path is not a directory: {self.path}")
            raise NotADirectoryError(f"Project path is not a directory: {self.path}")
            
        if not self.path.name.endswith(".scriv"):
            logger.error(f"Project path must end with .scriv: {self.path}")
            raise ValueError(f"Project path must end with .scriv: {self.path}")
        
        # Check for .scrivx file to ensure it's a valid project structure
        scrivx_files = list(self.path.glob("*.scrivx"))
        if not scrivx_files:
            logger.error(f"No .scrivx file found in project directory: {self.path}")
            raise ValueError(f"No .scrivx file found in project directory: {self.path}")
        
        self.scrivx_file = scrivx_files[0]
        logger.debug(f"Found .scrivx file: {self.scrivx_file}")
        
    def get_structure(self) -> dict:
        """
        Parses and returns the binder structure as a dictionary.
        """
        return {"binder": [node.to_dict() for node in self.nodes]}
        
    def get_document_path(self, uuid: str) -> Optional[Path]:
        """
        Returns the path to the content.rtf file for a given UUID.
        """
        return get_content_path(self.path, uuid)
        
    def read_document(self, uuid: str) -> str:
        """
        Reads the content of the document with the given UUID.
        
        Returns:
            The plain text content of the document.
            Returns empty string if document has no content file.
        """
        path = self.get_document_path(uuid)
        if not path or not path.exists():
            return ""
            
        try:
            # Scrivener RTF is often just standard ASCII 7-bit for control chars
            # content can be escaped. striprtf expects a string.
            # We open as utf-8 but handle errors just in case, though standard open is usually fine.
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                rtf_content = f.read()
                
            return convert_rtf_to_text(rtf_content)
        except Exception as e:
            logger.error(f"Error reading document {uuid}: {e}")
            return f"[Error reading document: {e}]"
            
    def update_metadata(self, uuid: str, field: str, value: str) -> None:
        """
        Updates metadata for a document and saves the project.
        """
        logger.debug(f"Updating metadata for document {uuid}: {field}={value}")
        self.metadata_manager.update_metadata(uuid, field, value)
        self.metadata_manager.save()
        
    def save_prompt(self, name: str, content: str) -> str:
        """Saves a prompt."""
        path = self.prompt_manager.save_prompt(name, content)
        return str(path)
        
    def get_prompt(self, name: str) -> Optional[str]:
        """Gets a prompt."""
        return self.prompt_manager.get_prompt(name)
        
    def list_prompts(self) -> List[str]:
        """Lists available prompts."""
        return self.prompt_manager.list_prompts()
        
    def save_summary(self, uuid: str, content: str) -> str:
        """Saves a summary definition."""
        path = self.summary_manager.save_summary(uuid, content)
        return str(path)
        
    def get_summary(self, uuid: str) -> Optional[str]:
        """Gets a summary."""
        return self.summary_manager.get_summary(uuid)
        
    def save_review(self, uuid: str, content: str) -> str:
        """Saves a style review."""
        path = self.review_manager.save_review(uuid, content)
        return str(path)
        
    def get_review(self, uuid: str) -> Optional[str]:
        """Gets a style review."""
    def get_review(self, uuid: str) -> Optional[str]:
        """Gets a style review."""
        return self.review_manager.get_review(uuid)

    # --- Character Management ---
    def save_character(self, name: str, content: str) -> str:
        """Saves a character profile."""
        # Use name as the key (not UUID) since these are likely new entities or manually named
        path = self.character_manager.save_data(name, content)
        return str(path)
        
    def get_character(self, name: str) -> Optional[str]:
        """Gets a character profile."""
        return self.character_manager.get_data(name)
        
    def list_characters(self) -> List[str]:
        """Lists available characters."""
        return self.character_manager.list_items()

    # --- Location Management ---
    def save_location(self, name: str, content: str) -> str:
        """Saves a location profile."""
        path = self.location_manager.save_data(name, content)
        return str(path)
        
    def get_location(self, name: str) -> Optional[str]:
        """Gets a location profile."""
        return self.location_manager.get_data(name)
        
    def list_locations(self) -> List[str]:
        """Lists available locations."""
        return self.location_manager.list_items()

    def __repr__(self):
        return f"<ScrivenerProject path='{self.path}'>"
