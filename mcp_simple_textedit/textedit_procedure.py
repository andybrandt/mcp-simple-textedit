import re
from typing import List, Dict, Union, Optional

class EditOperation:
    """Base class for edit operations"""
    def apply(self, lines: List[str]) -> List[str]:
        raise NotImplementedError()

class DeleteOperation(EditOperation):
    """Delete a block of text identified by patterns or line numbers"""
    def __init__(self, 
                 start_pattern: Optional[str] = None,
                 end_pattern: Optional[str] = None,
                 start_line: Optional[int] = None,
                 end_line: Optional[int] = None,
                 expected_content: Optional[str] = None):
        self.start_pattern = start_pattern
        self.end_pattern = end_pattern
        self.start_line = start_line
        self.end_line = end_line
        self.expected_content = expected_content

    def apply(self, lines: List[str]) -> List[str]:
        # Find start index
        if self.start_pattern:
            start_idx = next((i for i, line in enumerate(lines) 
                            if re.search(self.start_pattern, line)), -1)
            if start_idx == -1:
                raise ValueError(f"Start pattern '{self.start_pattern}' not found")
        else:
            start_idx = self.start_line - 1  # Convert to 0-based index

        # Find end index
        if self.end_pattern:
            end_idx = next((i for i in range(start_idx + 1, len(lines))
                          if re.search(self.end_pattern, lines[i])), -1)
            if end_idx == -1:
                raise ValueError(f"End pattern '{self.end_pattern}' not found")
        else:
            end_idx = self.end_line - 1 if self.end_line else start_idx

        # Verify content if specified
        if self.expected_content:
            actual_content = ''.join(lines[start_idx:end_idx + 1])
            if actual_content.strip() != self.expected_content.strip():
                raise ValueError("Content verification failed. Expected content not found.")

        # Return lines with the block removed
        return lines[:start_idx] + lines[end_idx + 1:]

class ReplaceOperation(EditOperation):
    """Replace a block of text identified by patterns or line numbers"""
    def __init__(self,
                 content: List[str],
                 start_pattern: Optional[str] = None,
                 end_pattern: Optional[str] = None,
                 start_line: Optional[int] = None,
                 end_line: Optional[int] = None,
                 expected_content: Optional[str] = None):
        self.content = content
        self.start_pattern = start_pattern
        self.end_pattern = end_pattern
        self.start_line = start_line
        self.end_line = end_line
        self.expected_content = expected_content

    def apply(self, lines: List[str]) -> List[str]:
        # Find start index
        if self.start_pattern:
            start_idx = next((i for i, line in enumerate(lines)
                            if re.search(self.start_pattern, line)), -1)
            if start_idx == -1:
                raise ValueError(f"Start pattern '{self.start_pattern}' not found")
        else:
            start_idx = self.start_line - 1

        # Find end index
        if self.end_pattern:
            end_idx = next((i for i in range(start_idx + 1, len(lines))
                          if re.search(self.end_pattern, lines[i])), -1)
            if end_idx == -1:
                raise ValueError(f"End pattern '{self.end_pattern}' not found")
        else:
            end_idx = self.end_line - 1 if self.end_line else start_idx

        # Verify content if specified
        if self.expected_content:
            actual_content = ''.join(lines[start_idx:end_idx + 1])
            if actual_content.strip() != self.expected_content.strip():
                raise ValueError("Content verification failed. Expected content not found.")

        # Return lines with the block replaced
        content_with_newlines = [
            line if line.endswith('\n') else line + '\n'
            for line in self.content
        ]
        return lines[:start_idx] + content_with_newlines + lines[end_idx + 1:]

class InsertOperation(EditOperation):
    """Insert text after a pattern or line number"""
    def __init__(self,
                 content: List[str],
                 after_pattern: Optional[str] = None,
                 before_pattern: Optional[str] = None,
                 after_line: Optional[int] = None,
                 expected_content: Optional[str] = None):
        self.content = content
        self.after_pattern = after_pattern
        self.before_pattern = before_pattern
        self.after_line = after_line
        self.expected_content = expected_content

    def apply(self, lines: List[str]) -> List[str]:
        # Find insertion point
        if self.after_pattern:
            insert_idx = next((i for i, line in enumerate(lines)
                             if re.search(self.after_pattern, line)), -1)
            if insert_idx == -1:
                raise ValueError(f"Pattern '{self.after_pattern}' not found")
        elif self.before_pattern:
            insert_idx = next((i - 1 for i, line in enumerate(lines)
                             if re.search(self.before_pattern, line)), -1)
            if insert_idx == -1:
                raise ValueError(f"Pattern '{self.before_pattern}' not found")
        else:
            insert_idx = self.after_line - 1

        # Verify content if specified
        if self.expected_content and insert_idx >= 0:
            if lines[insert_idx].strip() != self.expected_content.strip():
                raise ValueError("Content verification failed. Expected content not found.")

        # Return lines with new content inserted
        content_with_newlines = [
            line if line.endswith('\n') else line + '\n'
            for line in self.content
        ]
        return lines[:insert_idx + 1] + content_with_newlines + lines[insert_idx + 1:]

def create_operation(operation_dict: Dict) -> EditOperation:
    """Create an operation instance from a dictionary"""
    op_type = operation_dict["type"]
    
    if op_type == "delete":
        return DeleteOperation(
            start_pattern=operation_dict.get("start_pattern"),
            end_pattern=operation_dict.get("end_pattern"),
            start_line=operation_dict.get("start_line"),
            end_line=operation_dict.get("end_line"),
            expected_content=operation_dict.get("expected_content")
        )
    elif op_type == "replace":
        return ReplaceOperation(
            content=operation_dict["content"],
            start_pattern=operation_dict.get("start_pattern"),
            end_pattern=operation_dict.get("end_pattern"),
            start_line=operation_dict.get("start_line"),
            end_line=operation_dict.get("end_line"),
            expected_content=operation_dict.get("expected_content")
        )
    elif op_type == "insert":
        return InsertOperation(
            content=operation_dict["content"],
            after_pattern=operation_dict.get("after_pattern"),
            before_pattern=operation_dict.get("before_pattern"),
            after_line=operation_dict.get("after_line"),
            expected_content=operation_dict.get("expected_content")
        )
    else:
        raise ValueError(f"Unknown operation type: {op_type}")

def edit_text_file(file_path: str, operations: List[Dict]) -> None:
    """
    Edit a text file using pattern-based operations.
    
    Args:
        file_path: Path to the text file to edit
        operations: List of operations to perform. Each operation can use:
            - Patterns to find lines (start_pattern, end_pattern, after_pattern, before_pattern)
            - Line numbers (start_line, end_line, after_line)
            - Content verification (expected_content)
            
    Operations are processed in order. Line numbers are 1-based.
    """
    # Read file content
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Process operations
    for operation_dict in operations:
        operation = create_operation(operation_dict)
        lines = operation.apply(lines)
    
    # Write back
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        f.writelines(lines)