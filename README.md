# MCP Simple TextEdit

*An MCP server providing AI-optimized text editing capabilities.*

## Why Pattern-Based Editing?

While this text editor might seem unusual to humans who are comfortable with line numbers and visual editing, it's specifically designed for AI use. Here's why:

1. **AI Perception vs Human Perception**:
   - Humans naturally work with visual positions and line numbers
   - AIs perceive text through patterns, context, and content
   - AIs don't "see" the file but understand its structure

2. **Safety First**:
   - Line numbers can change when files are modified
   - Content-based identification is more robust
   - Pattern matching with verification prevents unintended changes

3. **Natural AI Workflow**:
   - AIs identify code sections by their meaning and context
   - AIs can verify they're modifying exactly what they intend to
   - Pattern matching aligns with how AIs process and understand text

This is why the editor supports:
- Pattern-based text block identification
- Content verification for safety
- Context-aware operations
- Regular expression matching

## Installation

First install the module using:

```bash
pip install mcp-simple-textedit
```

Then configure in the [Claude desktop app](https://claude.ai/download).

Under macOS, add this to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
"mcpServers": {
  "textedit": {
    "command": "python",
    "args": [
      "-m", 
      "mcp_simple_textedit",
      "--base-path",
      "/Users/YOUR_USERNAME/path/to/edit"
    ]
  }
}
```

Under Windows, first check your Python path using `where python` in cmd. Then add this to `%APPDATA%\Claude\claude_desktop_config.json`:

```json
"mcpServers": {
  "textedit": {
    "command": "C:\\Users\\YOUR_USERNAME\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
    "args": [
      "-m", 
      "mcp_simple_textedit",
      "--base-path",
      "C:\\Users\\YOUR_USERNAME\\path\\to\\edit"
    ]
  }
}
```

Replace YOUR_USERNAME with your actual username and adjust the base-path to the directory where you want to allow file editing. The server will only be able to edit files within this directory and its subdirectories.

## Security Features

The server enforces several security measures:
- Can only access files within the specified base directory
- Validates file paths to prevent directory traversal attacks
- Checks file permissions before attempting modifications
- Verifies content before making changes
- All file operations are logged for auditing purposes

## Text Encoding

All files are read and written using UTF-8 encoding. This ensures proper handling of:
- International characters
- Special symbols
- Emoji and other Unicode characters

If a file cannot be read or written using UTF-8, an appropriate error message will be provided.

## Pattern Matching Guidelines

For AIs using this tool, here are some guidelines for effective and safe text editing:

1. **Pattern Uniqueness**:
   ```python
   # Bad - ambiguous pattern
   {"start_pattern": "print(\"Done\")"}
   
   # Good - unique pattern with context
   {"start_pattern": "def process_data\\(\\):[\\s\\S]*?print\\(\"Done\"\\)"}
   ```

2. **Content Verification**:
   ```python
   # Good - verifies exact content being modified
   {
     "type": "replace",
     "start_pattern": "MAX_RETRIES = ",
     "expected_content": "MAX_RETRIES = 3",
     "content": ["MAX_RETRIES = 5"]
   }
   ```

3. **Block Operations**:
   ```python
   # Good - clear block identification
   {
     "type": "delete",
     "start_pattern": "# Old implementation",
     "end_pattern": "# End of old implementation",
     "expected_content": "# Old implementation\n    print(\"Processing...\")\n    # End of old implementation"
   }
   ```

4. **Context Awareness**:
   ```python
   # Good - uses surrounding context
   {
     "type": "insert",
     "after_pattern": "import logging\n",
     "content": ["import time", "from typing import List"]
   }
   ```

Remember: Always use `expected_content` when possible to verify you're modifying exactly what you intend to change.