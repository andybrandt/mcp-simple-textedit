"""Validation functions for the MCP Text Edit Server."""

import os
from pathlib import Path
from typing import Dict, List, Union

# Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_OPERATIONS = 1000  # Maximum operations per request

def validate_file_path(base_path: Union[str, Path], file_path: str) -> str:
    """
    Validate and resolve the file path, ensuring it's within the allowed directory.
    
    Args:
        base_path: Base directory for all operations
        file_path: Relative path to the file from the base directory
        
    Returns:
        Absolute path to the file
        
    Raises:
        ValueError: If the path is invalid or outside the allowed directory
    """
    try:
        # Convert paths to Path objects
        base_path = Path(base_path).resolve()
        abs_path = (base_path / file_path).resolve()
        
        # Check if the path is within the allowed directory
        if not str(abs_path).startswith(str(base_path)):
            raise ValueError("File path is outside the allowed directory")
        
        # Create parent directories if they don't exist
        abs_path.parent.mkdir(parents=True, exist_ok=True)

        # Create file if it doesn't exist
        if not abs_path.exists():
            abs_path.touch()
        elif not abs_path.is_file():
            raise ValueError("Path exists but is not a regular file")
        
        # Check if file is writable
        if not os.access(str(abs_path), os.W_OK):
            raise ValueError("File is not writable")

        # Check file size
        file_size = abs_path.stat().st_size
        if file_size > MAX_FILE_SIZE:
            raise ValueError(
                f"File size {file_size/1024/1024:.1f}MB exceeds maximum "
                f"allowed size {MAX_FILE_SIZE/1024/1024:.1f}MB"
            )
            
        return str(abs_path)
        
    except Exception as e:
        raise ValueError(f"Invalid file path: {str(e)}")

def validate_operations(operations: List[Dict]) -> List[Dict]:
    """
    Validate text editing operations list.
    
    Args:
        operations: List of operation dictionaries
        
    Returns:
        Validated operations list
        
    Raises:
        ValueError: If operations are invalid
    """
    if not operations:
        raise ValueError("No operations provided")

    # Check number of operations
    if len(operations) > MAX_OPERATIONS:
        raise ValueError(
            f"Number of operations ({len(operations)}) exceeds maximum "
            f"allowed ({MAX_OPERATIONS})"
        )

    # Basic type validation - detailed validation happens in implementation
    for op in operations:
        if "type" not in op:
            raise ValueError("Operation missing 'type' field")
        if op["type"] not in ["delete", "replace", "insert"]:
            raise ValueError(f"Invalid operation type: {op['type']}")
        
    return operations