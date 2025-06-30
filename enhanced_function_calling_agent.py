#!/usr/bin/env python3
"""
Enhanced Function Calling Agent with MCP Integration
Agent Engineering Bootcamp - Week 3 Assignment

This enhanced agent integrates MCP servers to provide additional tools
alongside the existing document search and web search capabilities.
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from litellm import completion
from dotenv import load_dotenv
from agent_tools import AgentTools
from cli_interface import CLIInterface
import platform
if platform.system() == "Windows":
    from mcp_client_windows_fix import WindowsMCPToolsWrapper as MCPToolsWrapper
else:
    from mcp_client import MCPToolsWrapper

load_dotenv()


class EnhancedFunctionCallingAgent:
    """
    Enhanced AI Agent with MCP integration and function calling capabilities.
    
    This agent can:
    1. Search through RAG documents (Tool 1) 
    2. Search the web for current information (Tool 2)
    3. Use MCP File System operations (Tools 3-7):
       - Read files
       - Write files  
       - List directories
       - Search file contents
       - Get file information
    """
    
    def __init__(self, cli: CLIInterface):
        """Initialize the enhanced function calling agent."""
        self.cli = cli
        
        # Initialize MCP integration
        self.mcp_tools = MCPToolsWrapper()
        self.mcp_enabled = False
        
        # Check OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable is required")
    
    def initialize_mcp(self, base_directory: str = ".") -> bool:
        """Initialize MCP tools."""
        try:
            self.cli.print_info("🔧 Initializing MCP File System Server...")
            success = self.mcp_tools.initialize(base_directory)
            if success:
                self.mcp_enabled = True
                self.cli.print_success("✅ MCP File System Server connected!")
                
                # Show available MCP tools
                mcp_tools = [tool for tool in self.get_available_tools() if "mcp_" in tool["function"]["name"]]
                if mcp_tools:
                    self.cli.print_info(f"📁 Available MCP tools: {', '.join([tool['function']['name'] for tool in mcp_tools])}")
                
                return True
            else:
                self.cli.print_warning("⚠️ Failed to connect to MCP server. Continuing with basic tools only.")
                return False
        except Exception as e:
            self.cli.print_warning(f"⚠️ MCP initialization failed: {e}. Continuing with basic tools only.")
            return False
    
    def get_available_tools(self) -> List[Dict]:
        """Get all available tools including both regular and MCP tools."""
        if self.mcp_enabled:
            return self.mcp_tools.get_available_tools()
        else:
            # Fallback to regular tools only
            regular_tools = AgentTools()
            return regular_tools.get_available_tools()
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute either a regular tool or an MCP tool."""
        if self.mcp_enabled:
            return self.mcp_tools.execute_tool(tool_name, **kwargs)
        else:
            # Fallback to regular tools only
            regular_tools = AgentTools()
            return regular_tools.execute_tool(tool_name, **kwargs)
    
    def chat_with_tools(self, user_message: str) -> str:
        """
        Main chat method that can use all available tools including MCP.
        
        Args:
            user_message (str): User's message/question
            
        Returns:
            str: AI response (potentially using tools)
        """
        try:
            self.cli.print_question(user_message)
            
            # Enhanced system message to guide the agent with MCP capabilities
            if self.mcp_enabled:
                system_message = """You are a helpful AI assistant with access to multiple tools:

1. search_documents: Search through uploaded documents (RAG)
2. search_web: Search the internet for current information
3. mcp_read_file: Read the contents of files
4. mcp_write_file: Write content to files (creates or overwrites)
5. mcp_list_directory: List contents of directories
6. mcp_search_files: Search for text within files in directories
7. mcp_file_info: Get information about files or directories

Use tools when appropriate to provide better answers. You can read, write, and manage files to help with various tasks."""
            else:
                system_message = """You are a helpful AI assistant with access to tools:

1. search_documents: Search through uploaded documents
2. search_web: Search the internet for current information

Use tools when appropriate to provide better answers."""

            # First call to get tool usage
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
            
            self.cli.loading_animation("Thinking", 1.5)
            
            # Get available tools
            available_tools = self.get_available_tools()
            
            # Call OpenAI with function calling
            response = completion(
                model="openai/gpt-4o",
                messages=messages,
                tools=available_tools,
                tool_choice="auto",
                temperature=0.7
            )
            
            response_message = response.choices[0].message
            
            # Check if the model wants to call functions
            tool_calls = getattr(response_message, 'tool_calls', None)
            
            if tool_calls:
                # Execute tool calls
                messages.append(response_message)
                
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    self.cli.print_info(f"Using tool: {function_name}")
                    self.cli.loading_animation(f"Executing {function_name}", 2.0)
                    
                    # Execute the tool
                    tool_result = self.execute_tool(function_name, **function_args)
                    
                    # Display tool results with enhanced MCP info
                    self._display_tool_results(function_name, tool_result)
                    
                    # Add tool result to conversation
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(tool_result)
                    })
                
                # Get final response from the model
                self.cli.loading_animation("Generating final response", 1.5)
                
                final_response = completion(
                    model="openai/gpt-4o",
                    messages=messages,
                    temperature=0.7
                )
                
                final_answer = final_response.choices[0].message.content
                
            else:
                # No tools needed, just return the response
                final_answer = response_message.content
            
            # Display the final answer
            self.cli.print_answer(final_answer)
            return final_answer
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.cli.print_error(error_msg)
            return "Sorry, I encountered an error."
    
    def _display_tool_results(self, tool_name: str, tool_result: Dict[str, Any]):
        """Display tool execution results in a nice format with MCP support."""
        if tool_result.get("success"):
            if tool_name.startswith("mcp_"):
                # MCP tool results
                result_text = tool_result.get("result", "")
                if tool_name == "mcp_list_directory":
                    self.cli.print_success("📁 Directory contents retrieved")
                elif tool_name == "mcp_read_file":
                    self.cli.print_success("📄 File read successfully")
                elif tool_name == "mcp_write_file":
                    self.cli.print_success("✏️ File written successfully")
                elif tool_name == "mcp_search_files":
                    self.cli.print_success("🔍 File search completed")
                elif tool_name == "mcp_file_info":
                    self.cli.print_success("ℹ️ File information retrieved")
                else:
                    self.cli.print_success(f"🔧 MCP tool {tool_name} executed")
            else:
                # Regular tool results
                results = tool_result.get("results", [])
                
                if tool_name == "search_documents":
                    self.cli.print_success(f"📚 Found {len(results)} documents")
                    
                elif tool_name == "search_web":
                    self.cli.print_success(f"🌐 Found {len(results)} web results")
        else:
            error = tool_result.get("error", "Unknown error")
            self.cli.print_warning(f"❌ Tool {tool_name} failed: {error}")
    
    def interactive_chat(self):
        """Start an interactive chat session with enhanced tool capabilities."""
        self.cli.print_info("🚀 Enhanced Function Calling Agent Ready!")
        
        # Initialize MCP if possible
        mcp_success = self.initialize_mcp()
        
        self.cli.print_info("Type 'quit' to exit.")
        
        # Show available tools
        available_tools = self.get_available_tools()
        tool_names = [tool["function"]["name"] for tool in available_tools]
        
        if self.mcp_enabled:
            regular_tools = [name for name in tool_names if not name.startswith("mcp_")]
            mcp_tools = [name for name in tool_names if name.startswith("mcp_")]
            
            self.cli.print_success(f"📋 Regular tools: {', '.join(regular_tools)}")
            self.cli.print_success(f"🔧 MCP tools: {', '.join(mcp_tools)}")
        else:
            self.cli.print_success(f"📋 Available tools: {', '.join(tool_names)}")
        
        while True:
            try:
                question = self.cli.get_user_input("What would you like to know")
                
                if question.lower() in ['quit', 'exit', 'q']:
                    self.cli.print_success("Chat session ended!")
                    break
                
                if not question.strip():
                    self.cli.print_warning("Please enter a question.")
                    continue
                
                self.chat_with_tools(question)
                self.cli.print_separator()
                
            except KeyboardInterrupt:
                self.cli.print_success("\nGoodbye!")
                break
            except Exception as e:
                self.cli.print_error(f"Error: {e}")
                continue
    
    def cleanup(self):
        """Clean up MCP resources."""
        if self.mcp_enabled:
            self.mcp_tools.cleanup()


if __name__ == "__main__":
    from cli_interface import CLIInterface
    
    cli = CLIInterface()
    agent = EnhancedFunctionCallingAgent(cli)
    
    try:
        agent.interactive_chat()
    finally:
        agent.cleanup() 