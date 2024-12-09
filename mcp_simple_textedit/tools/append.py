"""Append text operations for the MCP Text Edit Server."""

import os
from typing import List, Optional

def append_text(file_path: str, content: List[str], ensure_newline: bool = True) -> None:
    """
    Safely append text to the end of a file.
    
    Args:
        file_path: Path to the file to append to
        content: Lines of text to append
        ensure_newline: If True, ensures the file ends with a newline before appending
        
    Raises:
        ValueError: If content is empty or if file operations fail
    """
    if not content:
        raise ValueError("No content provided to append")

    try:
        # Check if file needs a newline at the end
        needs_newline = False
        if ensure_newline and os.path.getsize(file_path) > 0:
            with open(file_path, "r", encoding='utf-8') as f:
                f.seek(max(0, os.path.getsize(file_path) - 1))
                needs_newline = f.read(1) != '\n'
        
        # Append the content
        with open(file_path, "a", encoding='utf-8') as f:
            # Add newline if needed
            if needs_newline:
                f.write('\n')
            
            # Write content
            for line in content:
                f.write(line)
                if not line.endswith('\n'):
                    f.write('\n')

    except Exception as e:
        raise ValueError(f"Failed to append text: {str(e)}")