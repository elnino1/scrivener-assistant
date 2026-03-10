from pathlib import Path
from typing import List, Optional
import os
import logging
from scrivener_assistant.config import ProjectConfig

logger = logging.getLogger(__name__)

class PromptManager:
    """
    Manages loading and saving prompt files in the project's .ai-assistant directory.
    """
    
    def __init__(self, project_path: Path, config: Optional[ProjectConfig] = None):
        self.project_path = project_path
        self.config = config or ProjectConfig.default()
        self.prompts_dir = (
            self.project_path 
            / self.config.assistant_folder 
            / self.config.prompts_subfolder
        )
        logger.debug(f"PromptManager initialized for {project_path}, prompts_dir: {self.prompts_dir}")
        
    def _ensure_dir(self) -> None:
        if not self.prompts_dir.exists():
            logger.debug(f"Creating prompts directory: {self.prompts_dir}")
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        
    def save_prompt(self, name: str, content: str) -> Path:
        """
        Saves a prompt to a text file.
        """
        logger.debug(f"Saving prompt '{name}'")
        self._ensure_dir()
        
        # Sanitize name to avoid path traversal or weird chars
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
        if not safe_name:
            logger.error(f"Invalid prompt name: '{name}'")
            raise ValueError("Invalid prompt name")
            
        file_path = self.prompts_dir / f"{safe_name}.md"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info(f"Saved prompt '{name}' to {file_path}")
        return file_path

    def get_prompt(self, name: str) -> Optional[str]:
        """
        Retrieves the content of a prompt by name.
        """
        logger.debug(f"Retrieving prompt '{name}'")
        
        if not self.prompts_dir.exists():
            logger.debug(f"Prompts directory does not exist: {self.prompts_dir}")
            return None
            
        # Try finding exact match or with extension
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
        
        # Check .md and .txt
        candidates = [
            self.prompts_dir / f"{safe_name}.md",
            self.prompts_dir / f"{safe_name}.txt",
            self.prompts_dir / safe_name
        ]
        
        for p in candidates:
            if p.exists() and p.is_file():
                logger.debug(f"Found prompt '{name}' at {p}")
                return p.read_text(encoding="utf-8")
        
        logger.debug(f"Prompt '{name}' not found")
        return None

    def list_prompts(self) -> List[str]:
        """
        Returns a list of available prompt names.
        """
        if not self.prompts_dir.exists():
            return []
            
        prompts = []
        for f in self.prompts_dir.glob("*"):
            if f.is_file() and not f.name.startswith("."):
                prompts.append(f.stem)
        return sorted(prompts)
