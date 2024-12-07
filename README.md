# MCP Simple TextEdit

*When working in the Claude Desktop app, Claude needs to be able to edit text files in a precise way, modifying only specific lines while leaving the rest of the file untouched. This server provides that capability through a simple MCP tool.*

This server provides a text editing tool that can:
 - Delete specific lines from a text file
 - Replace specific lines with new content
 - Insert new lines after a specified line
 
The server handles text files using UTF-8 encoding, making it suitable for files containing text in various languages and special characters.

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

## Security Note

The server enforces several security measures:
- Can only access files within the specified base directory
- Validates file paths to prevent directory traversal attacks
- Checks file permissions before attempting modifications
- All file operations are logged for auditing purposes

## Text Encoding

All files are read and written using UTF-8 encoding. This ensures proper handling of:
- International characters
- Special symbols
- Emoji and other Unicode characters

If a file cannot be read or written using UTF-8, an appropriate error message will be provided.