from striprtf.striprtf import rtf_to_text

def convert_rtf_to_text(rtf_content: str) -> str:
    """
    Converts RTF content string to plain text.
    
    Args:
        rtf_content: The variable containing the RTF string.
        
    Returns:
        Cleaned plain text.
    """
    try:
        # rtf_to_text handles the grunt work of ignoring control words
        return rtf_to_text(rtf_content)
    except Exception as e:
        # Fallback or re-raise?
        # For an MCP server, returning error info in string might be safer 
        # than crashing, but let's re-raise to handle at service layer.
        raise ValueError(f"Failed to convert RTF: {e}")
