"""MCP server providing text editing capabilities."""

import os
import logging
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

from . import tools
from .tools import validate_file_path, validate_operations, append_text, edit_file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextEditServer:
    """MCP server providing text editing capabilities."""
    
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
                types.Tool(**tools.TOOL_SCHEMAS["edit_file"]),
                types.Tool(**tools.TOOL_SCHEMAS["append_text"])
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> Sequence[types.TextContent]:
            try:
                # Validate file path first
                file_path = validate_file_path(self.base_path, arguments["file_path"])
                
                if name == "edit_file":
                    # Validate and perform edit operations
                    operations = validate_operations(arguments["operations"])
                    edit_file(file_path, operations)
                    return [types.TextContent(
                        type="text",
                        text=f"Successfully edited file: {arguments['file_path']}"
                    )]
                    
                elif name == "append_text":
                    # Validate and perform append operation
                    append_text(
                        file_path, 
                        arguments["content"],
                        ensure_newline=arguments.get("ensure_newline", True)
                    )
                    return [types.TextContent(
                        type="text",
                        text=f"Successfully appended {len(arguments['content'])} lines to: {arguments['file_path']}"
                    )]
                    
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"Unknown tool: {name}",
                        isError=True
                    )]
                    
            except Exception as e:
                logger.error(f"Error in {name}: {str(e)}", exc_info=True)
                return [types.TextContent(
                    type="text",
                    text=f"Error: {str(e)}",
                    isError=True
                )]

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