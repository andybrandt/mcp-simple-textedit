"""Pattern-based text editing operations for the MCP Text Edit Server."""

import re
from typing import List, Dict, Optional, Tuple

def find_block(lines: List[str], pattern: str, start_from: int = 0) -> Optional[int]:
    """
    Find a line matching the pattern.
    
    Args:
        lines: List of lines to search
        pattern: Regular expression pattern to match
        start_from: Line index to start searching from
        
    Returns:
        Index of matching line or None if not found
    """
    for i in range(start_from, len(lines)):
        if re.search(pattern, lines[i]):
            return i
    return None

def verify_content(lines: List[str], start: int, end: int, expected: str) -> bool:
    """
    Verify that the specified block matches expected content.
    
    Args:
        lines: List of all lines
        start: Start index (inclusive)
        end: End index (inclusive)
        expected: Expected content
        
    Returns:
        True if content matches, False otherwise
    """
    actual = ''.join(lines[start:end + 1])
    return actual.strip() == expected.strip()

def process_operation(lines: List[str], operation: Dict) -> List[str]:
    """
    Process a single edit operation.
    
    Args:
        lines: Current file lines
        operation: Operation to perform
        
    Returns:
        Modified list of lines
        
    Raises:
        ValueError: If operation is invalid or cannot be performed
    """
    op_type = operation["type"]
    
    # Find the block to operate on
    start_idx = None
    end_idx = None
    
    if "start_pattern" in operation:
        start_idx = find_block(lines, operation["start_pattern"])
        if start_idx is None:
            raise ValueError(f"Start pattern '{operation['start_pattern']}' not found")
            
        if "end_pattern" in operation:
            end_idx = find_block(lines, operation["end_pattern"], start_idx + 1)
            if end_idx is None:
                raise ValueError(f"End pattern '{operation['end_pattern']}' not found")
    
    elif "after_pattern" in operation:
        start_idx = find_block(lines, operation["after_pattern"])
        if start_idx is None:
            raise ValueError(f"After pattern '{operation['after_pattern']}' not found")
        end_idx = start_idx
        
    elif "before_pattern" in operation:
        end_idx = find_block(lines, operation["before_pattern"])
        if end_idx is None:
            raise ValueError(f"Before pattern '{operation['before_pattern']}' not found")
        start_idx = end_idx - 1
        
    else:
        # Fall back to line numbers
        start_idx = operation.get("start_line", operation.get("after_line", 1)) - 1
        end_idx = operation.get("end_line", start_idx)
        
        if start_idx < 0 or end_idx >= len(lines):
            raise ValueError(f"Invalid line numbers: {start_idx + 1} to {end_idx + 1}")
    
    # Verify content if specified
    if "expected_content" in operation:
        if not verify_content(lines, start_idx, end_idx, operation["expected_content"]):
            raise ValueError("Content verification failed")
    
    # Perform the operation
    if op_type == "delete":
        return lines[:start_idx] + lines[end_idx + 1:]
        
    elif op_type == "replace":
        if "content" not in operation:
            raise ValueError("Replace operation requires content")
        content = [
            line if line.endswith('\n') else line + '\n'
            for line in operation["content"]
        ]
        return lines[:start_idx] + content + lines[end_idx + 1:]
        
    elif op_type == "insert":
        if "content" not in operation:
            raise ValueError("Insert operation requires content")
        content = [
            line if line.endswith('\n') else line + '\n'
            for line in operation["content"]
        ]
        return lines[:start_idx + 1] + content + lines[start_idx + 1:]
        
    else:
        raise ValueError(f"Unknown operation type: {op_type}")

def edit_file(file_path: str, operations: List[Dict]) -> None:
    """
    Edit a text file using pattern-based operations.
    
    Args:
        file_path: Path to the file to edit
        operations: List of edit operations to perform
        
    Raises:
        ValueError: If operations are invalid or fail
    """
    try:
        # Read the file
        with open(file_path, "r", encoding='utf-8') as f:
            lines = f.readlines()
        
        # Process operations in order
        for operation in operations:
            lines = process_operation(lines, operation)
        
        # Write back to file
        with open(file_path, "w", encoding='utf-8', newline='') as f:
            f.writelines(lines)
            
    except Exception as e:
        raise ValueError(f"Failed to edit file: {str(e)}")