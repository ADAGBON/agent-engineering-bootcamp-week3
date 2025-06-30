#!/usr/bin/env python3
"""
Enhanced Web Interface - Week 3 Assignment
Agent Engineering Bootcamp

A modern web interface showcasing MCP integration with file management capabilities.
"""

import os
import json
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from enhanced_function_calling_agent import EnhancedFunctionCallingAgent
from cli_interface import CLIInterface
import platform

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize enhanced agent
cli = CLIInterface()
agent = EnhancedFunctionCallingAgent(cli)

# Global variable to track agent initialization
agent_initialized = False

def initialize_agent():
    """Initialize the enhanced agent with MCP support."""
    global agent_initialized
    if not agent_initialized:
        try:
            # Initialize MCP - this will fall back gracefully if it fails
            agent.initialize_mcp()
            agent_initialized = True
            return True
        except Exception as e:
            print(f"Agent initialization warning: {e}")
            agent_initialized = True  # Still mark as initialized for fallback mode
            return False
    return True

@app.route('/')
def index():
    """Serve the enhanced web interface."""
    initialize_agent()
    
    # Get available tools for the UI
    tools = agent.get_available_tools()
    regular_tools = [tool for tool in tools if not tool["function"]["name"].startswith("mcp_")]
    mcp_tools = [tool for tool in tools if tool["function"]["name"].startswith("mcp_")]
    
    return render_template('enhanced_index.html', 
                         regular_tools=regular_tools,
                         mcp_tools=mcp_tools,
                         mcp_enabled=agent.mcp_enabled,
                         platform=platform.system())

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages with enhanced agent."""
    try:
        initialize_agent()
        
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Please enter a message'
            })
        
        # Get response from enhanced agent
        response = agent.chat_with_tools(user_message)
        
        return jsonify({
            'success': True,
            'response': response,
            'mcp_enabled': agent.mcp_enabled
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        })

@app.route('/tools')
def get_tools():
    """Get all available tools for the frontend."""
    try:
        initialize_agent()
        
        tools = agent.get_available_tools()
        regular_tools = [tool for tool in tools if not tool["function"]["name"].startswith("mcp_")]
        mcp_tools = [tool for tool in tools if tool["function"]["name"].startswith("mcp_")]
        
        return jsonify({
            'success': True,
            'regular_tools': regular_tools,
            'mcp_tools': mcp_tools,
            'mcp_enabled': agent.mcp_enabled,
            'total_tools': len(tools)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/file-explorer')
def file_explorer():
    """Get directory contents for file explorer."""
    try:
        initialize_agent()
        
        directory = request.args.get('directory', '.')
        
        # Use MCP tool if available, otherwise fallback
        if agent.mcp_enabled:
            result = agent.execute_tool("mcp_list_directory", directory_path=directory)
            if result["success"]:
                return jsonify({
                    'success': True,
                    'directory': directory,
                    'contents': result["result"]
                })
        
        return jsonify({
            'success': False,
            'error': 'File explorer requires MCP integration'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/read-file', methods=['POST'])
def read_file():
    """Read a file using MCP tools."""
    try:
        initialize_agent()
        
        data = request.get_json()
        file_path = data.get('file_path', '').strip()
        
        if not file_path:
            return jsonify({
                'success': False,
                'error': 'Please provide a file path'
            })
        
        if agent.mcp_enabled:
            result = agent.execute_tool("mcp_read_file", file_path=file_path)
            return jsonify(result)
        
        return jsonify({
            'success': False,
            'error': 'File reading requires MCP integration'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/write-file', methods=['POST'])
def write_file():
    """Write a file using MCP tools."""
    try:
        initialize_agent()
        
        data = request.get_json()
        file_path = data.get('file_path', '').strip()
        content = data.get('content', '')
        
        if not file_path:
            return jsonify({
                'success': False,
                'error': 'Please provide a file path'
            })
        
        if agent.mcp_enabled:
            result = agent.execute_tool("mcp_write_file", file_path=file_path, content=content)
            return jsonify(result)
        
        return jsonify({
            'success': False,
            'error': 'File writing requires MCP integration'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/search-files', methods=['POST'])
def search_files():
    """Search files using MCP tools."""
    try:
        initialize_agent()
        
        data = request.get_json()
        search_term = data.get('search_term', '').strip()
        directory = data.get('directory', '.')
        file_extension = data.get('file_extension', '')
        
        if not search_term:
            return jsonify({
                'success': False,
                'error': 'Please provide a search term'
            })
        
        if agent.mcp_enabled:
            result = agent.execute_tool("mcp_search_files", 
                                      search_term=search_term,
                                      directory_path=directory,
                                      file_extension=file_extension)
            return jsonify(result)
        
        return jsonify({
            'success': False,
            'error': 'File search requires MCP integration'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/status')
def status():
    """Get agent status and capabilities."""
    initialize_agent()
    
    return jsonify({
        'agent_initialized': agent_initialized,
        'mcp_enabled': agent.mcp_enabled,
        'platform': platform.system(),
        'tools_count': len(agent.get_available_tools()),
        'assignment': 'Week 3 - MCP Integration',
        'features': [
            'Document Search (RAG)',
            'Web Search',
            'File Reading (MCP)',
            'File Writing (MCP)',
            'Directory Listing (MCP)',
            'File Search (MCP)',
            'File Information (MCP)'
        ]
    })

if __name__ == '__main__':
    print("🚀 Starting Enhanced Web Interface - Week 3 Assignment")
    print("🔧 Agent Engineering Bootcamp - MCP Integration")
    print(f"🌐 Platform: {platform.system()}")
    
    try:
        initialize_agent()
        print(f"✅ Enhanced agent initialized (MCP enabled: {agent.mcp_enabled})")
        tools = agent.get_available_tools()
        print(f"🔧 Total tools available: {len(tools)}")
        
        mcp_tools = [tool for tool in tools if tool["function"]["name"].startswith("mcp_")]
        print(f"📁 MCP tools: {[tool['function']['name'] for tool in mcp_tools]}")
        
    except Exception as e:
        print(f"⚠️ Agent initialization warning: {e}")
    
    print("\n🌐 Enhanced Web Interface will be available at: http://localhost:5001")
    print("🎯 This showcases your Week 3 Assignment: Custom MCP Server Integration!")
    print("📁 Features: File management, enhanced chat, tool showcase")
    
    app.run(host='0.0.0.0', port=5001, debug=True) 