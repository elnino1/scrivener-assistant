import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, List
import logging
from scrivener_assistant.config import ProjectConfig

logger = logging.getLogger(__name__)

class MetadataManager:
    """
    Handles reading and modifying Scrivener project metadata (XML).
    """
    
    def __init__(self, scrivx_path: Path, config: Optional[ProjectConfig] = None):
        self.scrivx_path = scrivx_path
        self.config = config or ProjectConfig.default()
        
        logger.debug(f"Initializing MetadataManager for {scrivx_path}")
        
        if not self.scrivx_path.exists():
            logger.error(f"Scrivener project file not found: {self.scrivx_path}")
            raise FileNotFoundError(f"Scrivener project file not found: {self.scrivx_path}")
        
        # Load XML
        logger.debug(f"Parsing XML from {self.scrivx_path}")
        self.tree = ET.parse(self.scrivx_path)
        self.root = self.tree.getroot()
        logger.info(f"MetadataManager initialized successfully for {scrivx_path}")
    def _backup(self, max_backups: Optional[int] = None) -> None:
        """
        Perform a rolling backup of the .scrivx file.
        .scrivx -> .scrivx.bak.1
        .scrivx.bak.1 -> .scrivx.bak.2
        etc.
        """
        if max_backups is None:
            max_backups = self.config.max_backups
            
        # Shift existing backups
        # Iterate backwards: 4->5, 3->4, ...
        base = self.scrivx_path
        
        # Delete the oldest if it exists
        oldest = base.with_name(f"{base.name}.bak.{max_backups}")
        if oldest.exists():
            oldest.unlink()
            
        for i in range(max_backups - 1, 0, -1):
            src = base.with_name(f"{base.name}.bak.{i}")
            if src.exists():
                dest = base.with_name(f"{base.name}.bak.{i+1}")
                src.rename(dest)
        
        # Copy current file to .bak.1
        dest_first = base.with_name(f"{base.name}.bak.1")
        shutil.copy2(base, dest_first)
        logger.info(f"Created backup: {dest_first}")

    def save(self) -> None:
        """
        Saves the modified XML tree back to disk after creating a backup.
        """
        logger.debug(f"Saving metadata changes to {self.scrivx_path}")
        self._backup()
        
        # Write XML
        # Scrivener expects an XML declaration and UTF-8
        self.tree.write(self.scrivx_path, encoding="UTF-8", xml_declaration=True)
        logger.info(f"Saved changes to {self.scrivx_path}")

    def ensure_field_definition(self, field_name: str) -> str:
        """
        Ensures a Custom MetaData Field exists.
        Returns the FieldID.
        Checks both Scrivener native format (<Title>) and custom format (direct text).
        """
        logger.debug(f"Ensuring field definition for '{field_name}'")
        
        settings = self.root.find("CustomMetaDataSettings")
        if settings is None:
            logger.debug("CustomMetaDataSettings not found, creating new section")
            settings = ET.SubElement(self.root, "CustomMetaDataSettings")
            
        # Check existing fields in BOTH formats
        existing_fields = settings.findall("MetaDataField")
        
        for field in existing_fields:
            # Format 1: Scrivener native format with <Title> child element
            # Example: <MetaDataField ID="personnages"><Title>Personnages</Title></MetaDataField>
            title_elem = field.find("Title")
            if title_elem is not None and title_elem.text == field_name:
                field_id = field.get("ID")
                logger.debug(f"Found existing Scrivener field '{field_name}' with ID: {field_id}")
                return field_id
            
            # Format 2: Our custom format with direct text content
            # Example: <MetaDataField ID="Custom:Personnages">Personnages</MetaDataField>
            if field.text == field_name:
                field_id = field.get("ID")
                logger.debug(f"Found existing custom field '{field_name}' with ID: {field_id}")
                return field_id
                
        # Create new field only if not found in either format
        new_id = f"Custom:{field_name.replace(' ', '')}"
        
        logger.info(f"Creating new metadata field '{field_name}' with ID: {new_id}")
        
        # Verify ID uniqueness logic could be more robust, but simple for now
        
        new_field = ET.SubElement(settings, "MetaDataField")
        new_field.set("ID", new_id)
        new_field.set("Type", "Text") # Default to Text
        new_field.set("IncludeInCompile", "Yes") 
        new_field.set("FieldType", "Text") # For Scrivener 3?
        new_field.text = field_name
        
        logger.info(f"Created new metadata field '{field_name}' with ID: {new_id}")
        return new_id

    def update_metadata(self, uuid: str, field_name: str, value: str) -> None:
        """
        Updates (or creates) a metadata value for a specific Binder Item.
        """
        logger.debug(f"Updating metadata for UUID {uuid}: {field_name}={value}")
        
        # 1. Ensure the field definition exists
        field_id = self.ensure_field_definition(field_name)
        
        # 2. Find the BinderItem by UUID
        # Scrivener binder items can be nested deep.
        # XPath ".//BinderItem[@UUID='...']" finds it anywhere
        item = self.root.find(f".//BinderItem[@UUID='{uuid}']")
        if item is None:
            logger.error(f"BinderItem with UUID {uuid} not found")
            raise ValueError(f"BinderItem with UUID {uuid} not found.")
            
        # 3. Locate <MetaData><CustomMetaData>
        metadata = item.find("MetaData")
        if metadata is None:
            metadata = ET.SubElement(item, "MetaData")
            
        custom_metadata = metadata.find("CustomMetaData")
        if custom_metadata is None:
            custom_metadata = ET.SubElement(metadata, "CustomMetaData")
            
        # 4. Set the value
        # <MetaDataItem>
        #    <FieldID>Custom:Status</FieldID>
        #    <Value>Done</Value>
        # </MetaDataItem>
        
        # Check if value for this field already exists
        # We need to match based on FieldID child
        target_item = None
        for meta_item in custom_metadata.findall("MetaDataItem"):
            fid = meta_item.find("FieldID")
            if fid is not None and fid.text == field_id:
                target_item = meta_item
                break
        
        if target_item is None:
            target_item = ET.SubElement(custom_metadata, "MetaDataItem")
            fid = ET.SubElement(target_item, "FieldID")
            fid.text = field_id
            
        # Update Value
        val_elem = target_item.find("Value")
        if val_elem is None:
            val_elem = ET.SubElement(target_item, "Value")
        
        val_elem.text = value
        logger.info(f"Updated metadata {field_name}='{value}' for UUID {uuid}")
