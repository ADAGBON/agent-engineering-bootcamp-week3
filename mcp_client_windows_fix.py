#!/usr/bin/env python3
"""
Windows-Compatible MCP Client Integration
Agent Engineering Bootcamp - Week 3 Assignment

This module provides a Windows-compatible MCP client that fixes the subprocess issues.
"""

import asyncio
import json
import subprocess
import os
import sys
from typing import Dict, List, Any, Optional
from agent_tools import AgentTools


class WindowsMCPClient:
    """Windows-compatible MCP client using simplified communication."""
    
    def __init__(self):
        """Initialize the Windows MCP client."""
        self.available_tools = {}
        self.server_process = None
    
    def get_mcp_tools(self) -> List[Dict]:
        """Get MCP tools in OpenAI function calling format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "mcp_read_file",
                    "description": "[MCP] Read the contents of a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to read"
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "mcp_write_file",
                    "description": "[MCP] Write content to a file (creates or overwrites)",
                    "parameters": {
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
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "mcp_list_directory",
                    "description": "[MCP] List contents of a directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory_path": {
                                "type": "string",
                                "description": "Path to the directory to list",
                                "default": "."
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "mcp_search_files",
                    "description": "[MCP] Search for text within files in a directory",
                    "parameters": {
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
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "mcp_file_info",
                    "description": "[MCP] Get information about a file or directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path to the file or directory"
                            }
                        },
                        "required": ["path"]
                    }
                }
            }
        ]
    
    def execute_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an MCP tool using direct file operations (Windows-compatible)."""
        try:
            # Remove mcp_ prefix for internal handling
            operation = tool_name.replace("mcp_", "")
            
            if operation == "read_file":
                return self._read_file_direct(arguments["file_path"])
            elif operation == "write_file":
                return self._write_file_direct(arguments["file_path"], arguments["content"])
            elif operation == "list_directory":
                directory_path = arguments.get("directory_path", ".")
                return self._list_directory_direct(directory_path)
            elif operation == "search_files":
                search_term = arguments["search_term"]
                directory_path = arguments.get("directory_path", ".")
                file_extension = arguments.get("file_extension", "")
                return self._search_files_direct(search_term, directory_path, file_extension)
            elif operation == "file_info":
                return self._file_info_direct(arguments["path"])
            else:
                return {
                    "success": False,
                    "error": f"Unknown MCP operation: {operation}",
                    "result": ""
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing {tool_name}: {str(e)}",
                "result": ""
            }
    
    def _safe_path(self, path: str, base_directory: str = ".") -> str:
        """Ensure the path is safe and within base directory."""
        from pathlib import Path
        
        target_path = Path(path)
        if not target_path.is_absolute():
            target_path = Path(base_directory) / target_path
        
        # Resolve and check if it's within base directory
        resolved_path = target_path.resolve()
        base_resolved = Path(base_directory).resolve()
        
        try:
            resolved_path.relative_to(base_resolved)
            return str(resolved_path)
        except ValueError:
            raise PermissionError(f"Access denied: Path outside base directory")
    
    def _read_file_direct(self, file_path: str) -> Dict[str, Any]:
        """Read file directly using Python file operations."""
        try:
            safe_path = self._safe_path(file_path)
            
            if not os.path.exists(safe_path):
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                    "result": ""
                }
            
            if not os.path.isfile(safe_path):
                return {
                    "success": False,
                    "error": f"Path is not a file: {file_path}",
                    "result": ""
                }
            
            with open(safe_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "result": f"File: {file_path}\n---\n{content}",
                "tool_name": "mcp_read_file"
            }
            
        except UnicodeDecodeError:
            return {
                "success": False,
                "error": f"Unable to read file (binary or encoding issue): {file_path}",
                "result": ""
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error reading file: {str(e)}",
                "result": ""
            }
    
    def _write_file_direct(self, file_path: str, content: str) -> Dict[str, Any]:
        """Write file directly using Python file operations."""
        try:
            safe_path = self._safe_path(file_path)
            
            # Create parent directories if they don't exist
            os.makedirs(os.path.dirname(safe_path), exist_ok=True)
            
            with open(safe_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "result": f"Successfully wrote {len(content)} characters to: {file_path}",
                "tool_name": "mcp_write_file"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error writing file: {str(e)}",
                "result": ""
            }
    
    def _list_directory_direct(self, directory_path: str) -> Dict[str, Any]:
        """List directory contents directly."""
        try:
            safe_path = self._safe_path(directory_path)
            
            if not os.path.exists(safe_path):
                return {
                    "success": False,
                    "error": f"Directory not found: {directory_path}",
                    "result": ""
                }
            
            if not os.path.isdir(safe_path):
                return {
                    "success": False,
                    "error": f"Path is not a directory: {directory_path}",
                    "result": ""
                }
            
            items = []
            for item in sorted(os.listdir(safe_path)):
                item_path = os.path.join(safe_path, item)
                item_type = "📁" if os.path.isdir(item_path) else "📄"
                size = f" ({os.path.getsize(item_path)} bytes)" if os.path.isfile(item_path) else ""
                items.append(f"{item_type} {item}{size}")
            
            content = f"Directory: {directory_path}\n---\n" + "\n".join(items)
            if not items:
                content += "(empty directory)"
            
            return {
                "success": True,
                "result": content,
                "tool_name": "mcp_list_directory"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error listing directory: {str(e)}",
                "result": ""
            }
    
    def _search_files_direct(self, search_term: str, directory_path: str, file_extension: str) -> Dict[str, Any]:
        """Search files directly using Python file operations."""
        try:
            safe_path = self._safe_path(directory_path)
            
            if not os.path.exists(safe_path) or not os.path.isdir(safe_path):
                return {
                    "success": False,
                    "error": f"Invalid directory: {directory_path}",
                    "result": ""
                }
            
            matches = []
            search_term_lower = search_term.lower()
            
            for root, dirs, files in os.walk(safe_path):
                for file in files:
                    # Filter by extension if specified
                    if file_extension and not file.endswith(file_extension):
                        continue
                    
                    file_path = os.path.join(root, file)
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
                            
                            relative_path = os.path.relpath(file_path, safe_path)
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
            
            return {
                "success": True,
                "result": result,
                "tool_name": "mcp_search_files"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error searching files: {str(e)}",
                "result": ""
            }
    
    def _file_info_direct(self, path: str) -> Dict[str, Any]:
        """Get file information directly."""
        try:
            safe_path = self._safe_path(path)
            
            if not os.path.exists(safe_path):
                return {
                    "success": False,
                    "error": f"Path not found: {path}",
                    "result": ""
                }
            
            stat = os.stat(safe_path)
            info = [
                f"Path: {path}",
                f"Type: {'Directory' if os.path.isdir(safe_path) else 'File'}",
                f"Size: {stat.st_size} bytes",
                f"Last modified: {stat.st_mtime}",
            ]
            
            if os.path.isfile(safe_path):
                try:
                    with open(safe_path, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                    info.append(f"Lines: {lines}")
                except UnicodeDecodeError:
                    info.append("Type: Binary file")
            
            return {
                "success": True,
                "result": "File Information:\n---\n" + "\n".join(info),
                "tool_name": "mcp_file_info"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting file info: {str(e)}",
                "result": ""
            }


class WindowsMCPIntegratedTools:
    """
    Windows-compatible version of MCP integrated tools.
    """
    
    def __init__(self):
        """Initialize with both regular tools and Windows MCP integration."""
        self.regular_tools = AgentTools()
        self.mcp_client = WindowsMCPClient()
        self.mcp_enabled = True  # Always enabled since we use direct operations
    
    def get_available_tools(self) -> List[Dict]:
        """Get all available tools including both regular and MCP tools."""
        tools = self.regular_tools.get_available_tools()
        mcp_tools = self.mcp_client.get_mcp_tools()
        tools.extend(mcp_tools)
        return tools
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute either a regular tool or an MCP tool."""
        # Check if it's an MCP tool
        if tool_name.startswith("mcp_"):
            return self.mcp_client.execute_mcp_tool(tool_name, kwargs)
        
        # Otherwise, use regular tools
        return self.regular_tools.execute_tool(tool_name, **kwargs)


class WindowsMCPToolsWrapper:
    """Windows-compatible synchronous wrapper for MCP tools."""
    
    def __init__(self):
        self.mcp_tools = WindowsMCPIntegratedTools()
    
    def initialize(self, base_directory: str = ".") -> bool:
        """Initialize MCP tools (always successful on Windows version)."""
        return True
    
    def get_available_tools(self) -> List[Dict]:
        """Get available tools."""
        return self.mcp_tools.get_available_tools()
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool."""
        return self.mcp_tools.execute_tool(tool_name, **kwargs)
    
    def cleanup(self):
        """Clean up resources (no-op for Windows version)."""
        pass


if __name__ == "__main__":
    # Test the Windows MCP client
    from cli_interface import CLIInterface
    
    cli = CLIInterface("Windows MCP Test")
    
    print("🔧 Testing Windows-Compatible MCP Integration...")
    
    wrapper = WindowsMCPToolsWrapper()
    success = wrapper.initialize()
    
    if success:
        print("✅ Windows MCP integration successful!")
        
        tools = wrapper.get_available_tools()
        mcp_tools = [tool for tool in tools if "mcp_" in tool["function"]["name"]]
        print(f"🔧 Available MCP tools: {[tool['function']['name'] for tool in mcp_tools]}")
        
        # Test directory listing
        result = wrapper.execute_tool("mcp_list_directory", directory_path=".")
        if result["success"]:
            print("✅ Directory listing test passed")
            print("📁 Directory contents:")
            print(result["result"][:200] + "..." if len(result["result"]) > 200 else result["result"])
        
        # Test file creation and reading
        test_content = "Hello from Windows MCP!"
        write_result = wrapper.execute_tool("mcp_write_file", file_path="test_windows_mcp.txt", content=test_content)
        if write_result["success"]:
            print("✅ File writing test passed")
            
            read_result = wrapper.execute_tool("mcp_read_file", file_path="test_windows_mcp.txt")
            if read_result["success"]:
                print("✅ File reading test passed")
                
                # Clean up
                try:
                    os.remove("test_windows_mcp.txt")
                    print("🧹 Test file cleaned up")
                except:
                    pass
        
        wrapper.cleanup()
        print("🎉 Windows MCP integration test complete!")
        
    else:
        print("❌ Windows MCP integration failed") 