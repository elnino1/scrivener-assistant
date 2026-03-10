import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path

@dataclass
class BinderNode:
    """
    Represents a node in the Scrivener binder.
    """
    uuid: str
    title: str
    type: str # 'Folder', 'Text', 'DraftFolder', etc.
    children: List['BinderNode'] = field(default_factory=list)
    parent: Optional['BinderNode'] = field(default=None, repr=False)

    def get_path(self) -> List[str]:
        """Returns the list of folder/document titles from root down to this node."""
        path = []
        curr = self
        while curr:
            path.append(curr.title)
            curr = curr.parent
        return list(reversed(path))

    def to_dict(self) -> dict:
        """Recursive dictionary representation for JSON serialization."""
        return {
            "uuid": self.uuid,
            "title": self.title,
            "type": self.type,
            "children": [child.to_dict() for child in self.children]
        }

def _parse_binder_item(element: ET.Element) -> BinderNode:
    """
    Recursively parses a BinderItem element.
    """
    uuid = element.get("UUID")
    type_ = element.get("Type")
    
    # Find Title
    title_elem = element.find("Title")
    title = title_elem.text if title_elem is not None else "Untitled"
    
    node = BinderNode(uuid=uuid, title=title, type=type_)
    
    # Find Children
    children_elem = element.find("Children")
    if children_elem is not None:
        for child_elem in children_elem.findall("BinderItem"):
            child_node = _parse_binder_item(child_elem)
            child_node.parent = node
            node.children.append(child_node)
            
    return node

def parse_scrivx(scrivx_path: Path) -> List[BinderNode]:
    """
    Parses a .scrivx file and returns the root binder nodes.
    
    Args:
        scrivx_path: Path to the .scrivx file.
        
    Returns:
        List of top-level BinderNodes (usually Draft, Research, Trash).
    """
    if not scrivx_path.exists():
        raise FileNotFoundError(f"Scrivx file not found: {scrivx_path}")
        
    try:
        tree = ET.parse(scrivx_path)
        root = tree.getroot()
        
        binder_elem = root.find("Binder")
        if binder_elem is None:
            return []
            
        nodes = []
        for item in binder_elem.findall("BinderItem"):
            nodes.append(_parse_binder_item(item))
            
        return nodes
    except ET.ParseError as e:
        raise ValueError(f"Failed to parse .scrivx file: {e}")

def get_binder_map(nodes: List[BinderNode]) -> dict[str, BinderNode]:
    """Flattens the binder tree into a UUID -> BinderNode map."""
    binder_map = {}
    
    def _walk(node):
        binder_map[node.uuid] = node
        for child in node.children:
            _walk(child)
            
    for node in nodes:
        _walk(node)
        
    return binder_map
