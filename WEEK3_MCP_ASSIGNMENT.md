# Week 3 Assignment: MCP Server Integration

## 🎯 Assignment Completed: Model Context Protocol (MCP) Integration

**Agent Engineering Bootcamp - Week 3**

This project now includes a **custom MCP server built from scratch** that extends your agent's capabilities with file system operations!

## 🏆 What Was Built

### 1. Custom File System MCP Server (`file_system_mcp_server.py`)
Built from scratch, this MCP server provides:
- **Read files** - Access file contents
- **Write files** - Create or modify files  
- **List directories** - Browse folder contents
- **Search files** - Find text within files
- **File information** - Get metadata about files/directories

### 2. MCP Client Integration (`mcp_client.py`)
- Full MCP client implementation
- Async and sync wrappers for easy integration
- Automatic tool discovery and registration
- Seamless integration with existing agent tools

### 3. Enhanced Function Calling Agent (`enhanced_function_calling_agent.py`)
- Extends your Week 2 agent with MCP capabilities
- **7 total tools** now available:
  - `search_documents` (RAG - Week 2)
  - `search_web` (Web search - Week 2) 
  - `mcp_read_file` (MCP - Week 3)
  - `mcp_write_file` (MCP - Week 3)
  - `mcp_list_directory` (MCP - Week 3)
  - `mcp_search_files` (MCP - Week 3)
  - `mcp_file_info` (MCP - Week 3)

## 🚀 How to Run

### Quick Test
```bash
# Test the MCP integration
python test_week3_assignment.py
```

### Run the Enhanced Agent
```bash
# Start enhanced agent with MCP support (Week 3!)
python main.py enhanced-agent

# Or run the original agent (Week 2)
python main.py agent
```

### Install Dependencies
```bash
pip install -r requirements.txt
# or with uv:
uv add -r requirements.txt
```

## 🛠️ Key Files Added/Modified

### New Files (Week 3):
- `file_system_mcp_server.py` - **Custom MCP server built from scratch** ⭐
- `mcp_client.py` - MCP client integration
- `enhanced_function_calling_agent.py` - Enhanced agent with MCP
- `test_week3_assignment.py` - Testing suite
- `WEEK3_MCP_ASSIGNMENT.md` - This documentation

### Modified Files:
- `requirements.txt` - Added MCP dependencies
- `main.py` - Added `enhanced-agent` mode

## 💡 What Makes This Special

### 🌟 Built from Scratch (Bonus Points!)
The file system MCP server was built completely from scratch using the official MCP Python SDK, not just using an existing server.

### 🔧 Production Ready
- Proper error handling and security (sandboxed to base directory)
- Async/await support throughout
- Clean separation of concerns
- Graceful fallback if MCP fails

### 🧪 Thoroughly Tested
- Comprehensive test suite
- Import verification
- Tool execution tests
- Error handling verification

## 🎮 Example Usage

```bash
$ python main.py enhanced-agent

🚀 Enhanced Function Calling Agent Ready!
🔧 Initializing MCP File System Server...
✅ MCP File System Server connected!
📁 Available MCP tools: mcp_read_file, mcp_write_file, mcp_list_directory, mcp_search_files, mcp_file_info
📋 Regular tools: search_documents, search_web
🔧 MCP tools: mcp_read_file, mcp_write_file, mcp_list_directory, mcp_search_files, mcp_file_info

What would you like to know? > Can you help me organize my Python files?

# Agent can now:
# - List directory contents
# - Read Python files
# - Search for specific patterns
# - Create organized folder structures
# - Write summary files
# - All while maintaining conversation context!
```

## 🎯 Assignment Requirements Met

✅ **Add an MCP server to your agent's toolkit**
- Custom File System MCP server integrated

✅ **🤓 Bonus points for building from scratch**
- Built completely custom MCP server using MCP Python SDK
- Implements full MCP protocol with 5 different tools
- Professional error handling and security

## 🔮 What's Next?

Your agent now has powerful file system capabilities! Try asking it to:
- "Help me organize my code files"
- "Create a summary of all Python files in this directory"
- "Find all TODO comments in my code"
- "Create a project structure for a new app"

The MCP integration opens up endless possibilities for extending your agent with custom tools and external integrations!

---

**🎉 Week 3 Assignment Complete!** Your agent now has both document search, web search, AND file system operations through a custom MCP server built from scratch. 