#!/usr/bin/env python3
"""
MCP Client Integration
Agent Engineering Bootcamp - Week 3 Assignment

This module provides an MCP client that connects to our custom MCP servers
and makes their tools available to the function calling agent.
"""

import asyncio
import json
import subprocess
import os
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager
import mcp
from mcp.client.stdio import stdio_client


class MCPClient:
    """Client to connect to MCP servers and make their tools available."""
    
    def __init__(self):
        """Initialize the MCP client."""
        self.connected_servers = {}
        self.available_tools = {}
    
    async def connect_to_filesystem_server(self, base_directory: str = ".") -> bool:
        """Connect to the custom filesystem MCP server."""
        try:
            # Set environment variable for the server
            env = os.environ.copy()
            env["FS_MCP_BASE_DIR"] = base_directory
            
            # Start the MCP server as a subprocess
            server_process = await asyncio.create_subprocess_exec(
                "python", "file_system_mcp_server.py",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            # Connect using MCP client
            async with stdio_client(server_process.stdin, server_process.stdout) as client:
                # Initialize the connection
                await client.initialize()
                
                # Get available tools from the server
                tools_result = await client.list_tools()
                
                # Store the tools and connection info
                self.connected_servers["filesystem"] = {
                    "client": client,
                    "process": server_process
                }
                
                # Convert MCP tools to the format expected by our agent
                for tool in tools_result.tools:
                    tool_name = f"mcp_{tool.name}"  # Prefix to avoid conflicts
                    self.available_tools[tool_name] = {
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "description": f"[MCP] {tool.description}",
                            "parameters": tool.inputSchema
                        },
                        "mcp_server": "filesystem",
                        "original_name": tool.name
                    }
                
                return True
                
        except Exception as e:
            print(f"Error connecting to filesystem MCP server: {e}")
            return False
    
    def get_mcp_tools(self) -> List[Dict]:
        """Get all available MCP tools in OpenAI function calling format."""
        return [tool for tool in self.available_tools.values() if "mcp_server" in tool]
    
    async def execute_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an MCP tool and return the result."""
        try:
            if tool_name not in self.available_tools:
                return {
                    "success": False,
                    "error": f"Unknown MCP tool: {tool_name}",
                    "result": ""
                }
            
            tool_info = self.available_tools[tool_name]
            server_name = tool_info["mcp_server"]
            original_tool_name = tool_info["original_name"]
            
            if server_name not in self.connected_servers:
                return {
                    "success": False,
                    "error": f"MCP server {server_name} not connected",
                    "result": ""
                }
            
            client = self.connected_servers[server_name]["client"]
            
            # Execute the tool on the MCP server
            result = await client.call_tool(original_tool_name, arguments)
            
            # Extract text content from the result
            text_content = ""
            if result.content:
                for content in result.content:
                    if hasattr(content, 'text'):
                        text_content += content.text + "\n"
            
            return {
                "success": True,
                "result": text_content.strip(),
                "tool_name": tool_name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing MCP tool {tool_name}: {str(e)}",
                "result": ""
            }
    
    def is_mcp_tool(self, tool_name: str) -> bool:
        """Check if a tool name is an MCP tool."""
        return tool_name.startswith("mcp_") and tool_name in self.available_tools
    
    async def cleanup(self):
        """Clean up connections to MCP servers."""
        for server_name, server_info in self.connected_servers.items():
            try:
                if "process" in server_info:
                    server_info["process"].terminate()
                    await server_info["process"].wait()
            except Exception as e:
                print(f"Error cleaning up MCP server {server_name}: {e}")
        
        self.connected_servers.clear()
        self.available_tools.clear()


class MCPIntegratedTools:
    """
    Enhanced version of AgentTools that includes MCP server capabilities.
    This is the main interface for Week 3 assignment.
    """
    
    def __init__(self):
        """Initialize with both regular tools and MCP integration."""
        # Import here to avoid circular imports
        from agent_tools import AgentTools
        
        self.regular_tools = AgentTools()
        self.mcp_client = MCPClient()
        self.mcp_connected = False
    
    async def initialize_mcp(self, base_directory: str = ".") -> bool:
        """Initialize MCP connections."""
        try:
            success = await self.mcp_client.connect_to_filesystem_server(base_directory)
            self.mcp_connected = success
            return success
        except Exception as e:
            print(f"Failed to initialize MCP: {e}")
            return False
    
    def get_available_tools(self) -> List[Dict]:
        """Get all available tools including both regular and MCP tools."""
        tools = self.regular_tools.get_available_tools()
        
        if self.mcp_connected:
            mcp_tools = self.mcp_client.get_mcp_tools()
            tools.extend(mcp_tools)
        
        return tools
    
    async def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute either a regular tool or an MCP tool."""
        # Check if it's an MCP tool
        if self.mcp_connected and self.mcp_client.is_mcp_tool(tool_name):
            return await self.mcp_client.execute_mcp_tool(tool_name, kwargs)
        
        # Otherwise, use regular tools
        return self.regular_tools.execute_tool(tool_name, **kwargs)
    
    async def cleanup(self):
        """Clean up MCP connections."""
        if self.mcp_connected:
            await self.mcp_client.cleanup()


# Synchronous wrapper for easier integration
class MCPToolsWrapper:
    """Synchronous wrapper for MCP tools to integrate with existing code."""
    
    def __init__(self):
        self.mcp_tools = None
        self._loop = None
    
    def initialize(self, base_directory: str = ".") -> bool:
        """Initialize MCP tools synchronously."""
        try:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            
            self.mcp_tools = MCPIntegratedTools()
            success = self._loop.run_until_complete(
                self.mcp_tools.initialize_mcp(base_directory)
            )
            return success
        except Exception as e:
            print(f"Failed to initialize MCP wrapper: {e}")
            return False
    
    def get_available_tools(self) -> List[Dict]:
        """Get available tools."""
        if not self.mcp_tools:
            return []
        return self.mcp_tools.get_available_tools()
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool synchronously."""
        if not self.mcp_tools or not self._loop:
            return {"success": False, "error": "MCP not initialized"}
        
        try:
            return self._loop.run_until_complete(
                self.mcp_tools.execute_tool(tool_name, **kwargs)
            )
        except Exception as e:
            return {"success": False, "error": f"Error executing tool: {str(e)}"}
    
    def cleanup(self):
        """Clean up resources."""
        if self.mcp_tools and self._loop:
            self._loop.run_until_complete(self.mcp_tools.cleanup())
        if self._loop:
            self._loop.close()


if __name__ == "__main__":
    # Test the MCP client
    async def test_mcp():
        mcp_tools = MCPIntegratedTools()
        
        print("🔧 Testing MCP Integration...")
        success = await mcp_tools.initialize_mcp()
        
        if success:
            print("✅ MCP server connected successfully!")
            
            tools = mcp_tools.get_available_tools()
            print(f"📋 Available tools: {len(tools)}")
            
            for tool in tools:
                if "mcp" in tool["function"]["name"]:
                    print(f"  🔧 {tool['function']['name']}: {tool['function']['description']}")
            
            # Test file listing
            result = await mcp_tools.execute_tool("mcp_list_directory", directory_path=".")
            if result["success"]:
                print("🗂️  Directory listing:")
                print(result["result"])
            
        else:
            print("❌ Failed to connect to MCP server")
        
        await mcp_tools.cleanup()
    
    asyncio.run(test_mcp()) 