#!/usr/bin/env python3
"""
Custom File System MCP Server
Agent Engineering Bootcamp - Week 3 Assignment

This MCP server provides file system operations to AI agents:
- Read files and directories
- Write and create files
- Search file contents
- Basic file management operations
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Any, Sequence, Optional
import mcp.types as types
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio


class FileSystemMCPServer:
    """Custom File System MCP Server implementation."""
    
    def __init__(self, base_directory: str = "."):
        """Initialize the server with a base directory for safety."""
        self.base_directory = Path(base_directory).resolve()
        self.server = Server("filesystem")
        self._setup_tools()
    
    def _setup_tools(self):
        """Set up all the tools that this MCP server provides."""
        
        # Tool 1: Read File
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            return [
                types.Tool(
                    name="read_file",
                    description="Read the contents of a file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to read"
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                types.Tool(
                    name="write_file",
                    description="Write content to a file (creates or overwrites)",
                    inputSchema={
                        "type": "object", 
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to write"
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to write to the file"
                            }
                        },
                        "required": ["file_path", "content"]
                    }
                ),
                types.Tool(
                    name="list_directory",
                    description="List contents of a directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "directory_path": {
                                "type": "string", 
                                "description": "Path to the directory to list",
                                "default": "."
                            }
                        }
                    }
                ),
                types.Tool(
                    name="search_files",
                    description="Search for text within files in a directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "search_term": {
                                "type": "string",
                                "description": "Text to search for"
                            },
                            "directory_path": {
                                "type": "string",
                                "description": "Directory to search in",
                                "default": "."
                            },
                            "file_extension": {
                                "type": "string", 
                                "description": "File extension to filter by (e.g., '.py', '.txt')",
                                "default": ""
                            }
                        },
                        "required": ["search_term"]
                    }
                ),
                types.Tool(
                    name="file_info",
                    description="Get information about a file or directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path to the file or directory"
                            }
                        },
                        "required": ["path"]
                    }
                )
            ]
        
        # Tool implementations
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
            try:
                if name == "read_file":
                    return await self._read_file(arguments["file_path"])
                elif name == "write_file":
                    return await self._write_file(arguments["file_path"], arguments["content"])
                elif name == "list_directory":
                    directory_path = arguments.get("directory_path", ".")
                    return await self._list_directory(directory_path)
                elif name == "search_files":
                    search_term = arguments["search_term"]
                    directory_path = arguments.get("directory_path", ".")
                    file_extension = arguments.get("file_extension", "")
                    return await self._search_files(search_term, directory_path, file_extension)
                elif name == "file_info":
                    return await self._file_info(arguments["path"])
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]
    
    def _safe_path(self, path: str) -> Path:
        """Ensure the path is within the base directory for security."""
        target_path = Path(path)
        if not target_path.is_absolute():
            target_path = self.base_directory / target_path
        
        # Resolve and check if it's within base directory
        resolved_path = target_path.resolve()
        
        try:
            resolved_path.relative_to(self.base_directory)
            return resolved_path
        except ValueError:
            raise PermissionError(f"Access denied: Path outside base directory")
    
    async def _read_file(self, file_path: str) -> list[types.TextContent]:
        """Read the contents of a file."""
        try:
            safe_path = self._safe_path(file_path)
            
            if not safe_path.exists():
                return [types.TextContent(
                    type="text", 
                    text=f"Error: File not found: {file_path}"
                )]
            
            if not safe_path.is_file():
                return [types.TextContent(
                    type="text",
                    text=f"Error: Path is not a file: {file_path}"
                )]
            
            with open(safe_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return [types.TextContent(
                type="text",
                text=f"File: {file_path}\n---\n{content}"
            )]
            
        except UnicodeDecodeError:
            return [types.TextContent(
                type="text",
                text=f"Error: Unable to read file (binary or encoding issue): {file_path}"
            )]
        except Exception as e:
            return [types.TextContent(
                type="text", 
                text=f"Error reading file: {str(e)}"
            )]
    
    async def _write_file(self, file_path: str, content: str) -> list[types.TextContent]:
        """Write content to a file."""
        try:
            safe_path = self._safe_path(file_path)
            
            # Create parent directories if they don't exist
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(safe_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return [types.TextContent(
                type="text",
                text=f"Successfully wrote {len(content)} characters to: {file_path}"
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error writing file: {str(e)}"
            )]
    
    async def _list_directory(self, directory_path: str) -> list[types.TextContent]:
        """List contents of a directory."""
        try:
            safe_path = self._safe_path(directory_path)
            
            if not safe_path.exists():
                return [types.TextContent(
                    type="text",
                    text=f"Error: Directory not found: {directory_path}"
                )]
            
            if not safe_path.is_dir():
                return [types.TextContent(
                    type="text", 
                    text=f"Error: Path is not a directory: {directory_path}"
                )]
            
            items = []
            for item in sorted(safe_path.iterdir()):
                item_type = "📁" if item.is_dir() else "📄"
                size = f" ({item.stat().st_size} bytes)" if item.is_file() else ""
                items.append(f"{item_type} {item.name}{size}")
            
            content = f"Directory: {directory_path}\n---\n" + "\n".join(items)
            if not items:
                content += "(empty directory)"
            
            return [types.TextContent(type="text", text=content)]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error listing directory: {str(e)}"
            )]
    
    async def _search_files(self, search_term: str, directory_path: str, file_extension: str) -> list[types.TextContent]:
        """Search for text within files."""
        try:
            safe_path = self._safe_path(directory_path)
            
            if not safe_path.exists() or not safe_path.is_dir():
                return [types.TextContent(
                    type="text",
                    text=f"Error: Invalid directory: {directory_path}"
                )]
            
            matches = []
            search_term_lower = search_term.lower()
            
            for file_path in safe_path.rglob("*"):
                if not file_path.is_file():
                    continue
                    
                # Filter by extension if specified
                if file_extension and not file_path.name.endswith(file_extension):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    if search_term_lower in content.lower():
                        # Find line numbers with matches
                        lines = content.split('\n')
                        matching_lines = []
                        for i, line in enumerate(lines, 1):
                            if search_term_lower in line.lower():
                                matching_lines.append(f"  Line {i}: {line.strip()}")
                        
                        relative_path = file_path.relative_to(safe_path)
                        matches.append(f"📄 {relative_path}:")
                        matches.extend(matching_lines[:3])  # Show first 3 matches
                        if len(matching_lines) > 3:
                            matches.append(f"  ... and {len(matching_lines) - 3} more matches")
                        matches.append("")  # Empty line for separation
                        
                except (UnicodeDecodeError, PermissionError):
                    continue  # Skip binary files or files we can't read
            
            if matches:
                result = f"Search results for '{search_term}' in {directory_path}:\n---\n" + "\n".join(matches)
            else:
                result = f"No matches found for '{search_term}' in {directory_path}"
            
            return [types.TextContent(type="text", text=result)]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error searching files: {str(e)}"
            )]
    
    async def _file_info(self, path: str) -> list[types.TextContent]:
        """Get information about a file or directory."""
        try:
            safe_path = self._safe_path(path)
            
            if not safe_path.exists():
                return [types.TextContent(
                    type="text",
                    text=f"Error: Path not found: {path}"
                )]
            
            stat = safe_path.stat()
            info = [
                f"Path: {path}",
                f"Type: {'Directory' if safe_path.is_dir() else 'File'}",
                f"Size: {stat.st_size} bytes",
                f"Last modified: {stat.st_mtime}",
                f"Permissions: {oct(stat.st_mode)[-3:]}"
            ]
            
            if safe_path.is_file():
                try:
                    with open(safe_path, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                    info.append(f"Lines: {lines}")
                except UnicodeDecodeError:
                    info.append("Type: Binary file")
            
            return [types.TextContent(
                type="text",
                text="File Information:\n---\n" + "\n".join(info)
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error getting file info: {str(e)}"
            )]
    
    async def run(self):
        """Run the MCP server."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="filesystem",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities={}
                    )
                )
            )


async def main():
    """Main function to start the MCP server."""
    # You can specify a different base directory here
    base_dir = os.getenv("FS_MCP_BASE_DIR", ".")
    server = FileSystemMCPServer(base_dir)
    await server.run()


if __name__ == "__main__":
    asyncio.run(main()) 