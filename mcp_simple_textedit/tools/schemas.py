"""JSON schemas and descriptions for MCP Text Edit Server tools."""

# Schema for the experimental edit_file tool
EDIT_FILE_SCHEMA = {
    "type": "object",
    "properties": {
        "file_path": {
            "type": "string",
            "description": "Relative path to the text file from the base directory"
        },
        "operations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["delete", "replace", "insert"],
                        "description": "Type of operation to perform"
                    },
                    "start_pattern": {
                        "type": "string",
                        "description": "Regular expression pattern to identify start of text block.\n"
                                    "Include surrounding context to ensure uniqueness.\n"
                                    "Example: 'def process_data\\\\(\\\\):\\\\s*'"
                    },
                    "end_pattern": {
                        "type": "string",
                        "description": "Regular expression pattern to identify end of text block.\n"
                                    "Example: '    return result'"
                    },
                    "after_pattern": {
                        "type": "string",
                        "description": "Pattern identifying line after which to insert.\n"
                                    "Example: 'import sys\\n'"
                    },
                    "before_pattern": {
                        "type": "string",
                        "description": "Pattern identifying line before which to insert.\n"
                                    "Example: 'def main()'"
                    },
                    "start_line": {
                        "type": "integer",
                        "description": "Starting line number (1-based) for operations.\n"
                                    "Use only when pattern matching isn't suitable."
                    },
                    "end_line": {
                        "type": "integer",
                        "description": "Ending line number (1-based) for operations.\n"
                                    "Defaults to start_line if not specified."
                    },
                    "after_line": {
                        "type": "integer",
                        "description": "Line number after which to insert content.\n"
                                    "Use only when pattern matching isn't suitable."
                    },
                    "content": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "New lines of text to insert or use as replacement.\n"
                                    "Each array element is one line of text.\n"
                                    "Maintain proper indentation for the file structure."
                    },
                    "expected_content": {
                        "type": "string",
                        "description": "Exact content expected to be found for verification.\n"
                                    "Strongly recommended to prevent unintended changes.\n"
                                    "Should include all lines that will be modified."
                    }
                },
                "required": ["type"]
            }
        }
    },
    "required": ["file_path", "operations"]
}

# Schema for the safe append_text tool
APPEND_TEXT_SCHEMA = {
    "type": "object",
    "properties": {
        "file_path": {
            "type": "string",
            "description": "Relative path to the text file from the base directory"
        },
        "content": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Lines of text to append. Each array element will be added as a new line."
        },
        "ensure_newline": {
            "type": "boolean",
            "description": "If true, ensures the file ends with a newline before appending (default: true)",
            "default": True
        }
    },
    "required": ["file_path", "content"]
}

# Tool descriptions
TOOL_DESCRIPTIONS = {
    "edit_file": "[EXPERIMENTAL] Edit text files using pattern matching - use with caution.\n\n"
                "WARNING: This tool's pattern-based editing can lead to unintended changes or file corruption.\n"
                "Always verify changes and have backups. For safe text addition, use append_text instead.\n\n"
                "This tool allows pattern-based text modification with these features:\n"
                "1. Pattern Matching: Use regex patterns to identify text blocks\n"
                "2. Content Verification: Verify content before changes\n"
                "3. Block Operations: Delete, replace, or insert text blocks",

    "append_text": "Safely add text to the end of a file.\n\n"
                "This is a safe operation that simply adds the provided text\n"
                "at the end of the specified file. Useful for logs, notes,\n"
                "or any content that should be added sequentially."
}

# Complete tool schema definitions
TOOL_SCHEMAS = {
    "edit_file": {
        "name": "edit_file",
        "description": TOOL_DESCRIPTIONS["edit_file"],
        "inputSchema": EDIT_FILE_SCHEMA
    },
    "append_text": {
        "name": "append_text",
        "description": TOOL_DESCRIPTIONS["append_text"],
        "inputSchema": APPEND_TEXT_SCHEMA
    }
}