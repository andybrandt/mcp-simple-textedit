import os
import logging
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence
from dataclasses import dataclass

from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

from .textedit_procedure import edit_text_file

# Server configuration constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_OPERATIONS = 1000  # Maximum number of operations per request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextEditServer:
    def __init__(self, base_path: str):
        """Initialize the text edit server with a base path."""
        self.base_path = Path(base_path).resolve()
        self.server = Server("text-edit-server")
        self.setup_tools()

    def setup_tools(self):
        """Set up the server tools."""
        @self.server.list_tools()
        async def list_tools() -> list[types.Tool]:
            return [
                types.Tool(
                    name="get_config",
                    description="Get server configuration information",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="edit_file",
                    description="Edit a text file using pattern-based or line-based operations",
                    inputSchema={
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
                                        # Pattern-based identification
                                        "start_pattern": {
                                            "type": "string",
                                            "description": "Pattern to identify start line (delete/replace)"
                                        },
                                        "end_pattern": {
                                            "type": "string",
                                            "description": "Pattern to identify end line (delete/replace)"
                                        },
                                        "after_pattern": {
                                            "type": "string",
                                            "description": "Pattern to identify line after which to insert"
                                        },
                                        "before_pattern": {
                                            "type": "string",
                                            "description": "Pattern to identify line before which to insert"
                                        },
                                        # Line number identification (fallback)
                                        "start_line": {
                                            "type": "integer",
                                            "description": "Starting line number (delete/replace)"
                                        },
                                        "end_line": {
                                            "type": "integer",
                                            "description": "Ending line number (delete/replace)"
                                        },
                                        "after_line": {
                                            "type": "integer",
                                            "description": "Line number after which to insert"
                                        },
                                        # Content
                                        "content": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "Lines of text to insert or replace with"
                                        },
                                        # Verification
                                        "expected_content": {
                                            "type": "string",
                                            "description": "Expected content for verification"
                                        }
                                    },
                                    "required": ["type"]
                                }
                            }
                        },
                        "required": ["file_path", "operations"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> Sequence[types.TextContent]:
            if name == "get_config":
                return [types.TextContent(
                    type="text",
                    text=f"Text Edit Server Configuration:\n"
                         f"Base Path: {self.base_path}\n"
                         f"Encoding: UTF-8\n"
                         f"Maximum file size: {MAX_FILE_SIZE/1024/1024:.1f}MB\n"
                         f"Maximum operations per request: {MAX_OPERATIONS}\n"
                         f"Features:\n"
                         f"- Pattern-based line identification\n"
                         f"- Expected content verification\n"
                         f"- Line number fallback"
                )]
            elif name == "edit_file":
                try:
                    # Validate and resolve the file path
                    file_path = self._validate_file_path(arguments["file_path"])
                    
                    # Validate operations
                    operations = self._validate_operations(arguments["operations"])

                    # Perform the edit operations
                    edit_text_file(file_path, operations)

                    return [types.TextContent(
                        type="text",
                        text=f"Successfully edited file: {arguments['file_path']}"
                    )]

                except Exception as e:
                    logger.error(f"Error editing file: {str(e)}", exc_info=True)
                    return [types.TextContent(
                        type="text",
                        text=f"Error editing file: {str(e)}",
                        isError=True
                    )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Unknown tool: {name}",
                    isError=True
                )]

    def _validate_file_path(self, file_path: str) -> str:
        """
        Validate and resolve the file path, ensuring it's within the allowed directory.
        
        Args:
            file_path: Relative path to the file from the base directory
            
        Returns:
            Absolute path to the file
            
        Raises:
            ValueError: If the path is invalid or outside the allowed directory
        """
        try:
            # Convert to absolute path
            abs_path = (self.base_path / file_path).resolve()
            
            # Check if the path is within the allowed directory
            if not str(abs_path).startswith(str(self.base_path)):
                raise ValueError("File path is outside the allowed directory")
            
            # Check if file exists and is a regular file
            if not abs_path.is_file():
                raise ValueError("File does not exist or is not a regular file")
            
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

    def _validate_operations(self, operations: List[Dict]) -> List[Dict]:
        """Validate and normalize the edit operations."""
        if not operations:
            raise ValueError("No operations provided")

        # Check number of operations
        if len(operations) > MAX_OPERATIONS:
            raise ValueError(
                f"Number of operations ({len(operations)}) exceeds maximum "
                f"allowed ({MAX_OPERATIONS})"
            )

        # Basic type validation - detailed validation happens in edit_text_file
        for op in operations:
            if "type" not in op:
                raise ValueError("Operation missing 'type' field")
            if op["type"] not in ["delete", "replace", "insert"]:
                raise ValueError(f"Invalid operation type: {op['type']}")
            
        return operations

    async def run(self):
        """Run the text edit server."""
        async with stdio_server() as streams:
            await self.server.run(
                streams[0],
                streams[1],
                self.server.create_initialization_options()
            )

def main():
    """Main entry point for the text edit server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Text Edit Server")
    parser.add_argument(
        "--base-path", 
        type=str, 
        required=True,
        help="Base directory path for file operations"
    )
    
    args = parser.parse_args()
    
    try:
        base_path = Path(args.base_path).resolve()
        if not base_path.is_dir():
            raise ValueError(
                f"Base path does not exist or is not a directory: {args.base_path}"
            )
        
        server = TextEditServer(args.base_path)
        asyncio.run(server.run())
        
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()