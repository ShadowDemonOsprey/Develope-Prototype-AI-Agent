"""
Tool registry and base tool implementations.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, Field
import asyncio
import logging

logger = logging.getLogger(__name__)


class ToolResult(BaseModel):
    """Result of a tool execution."""
    success: bool
    output: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Tool(BaseModel, ABC):
    """Base class for all tools."""
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters."""
        pass

    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate input parameters."""
        return True


class ToolRegistry:
    """Registry for managing available tools."""
    
    _tools: Dict[str, Tool] = {}
    
    @classmethod
    def register(cls, tool: Tool) -> None:
        """Register a tool."""
        cls._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    @classmethod
    def unregister(cls, name: str) -> None:
        """Unregister a tool."""
        if name in cls._tools:
            del cls._tools[name]
            logger.info(f"Unregistered tool: {name}")
    
    @classmethod
    def get(cls, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return cls._tools.get(name)
    
    @classmethod
    def list_tools(cls) -> List[Tool]:
        """List all registered tools."""
        return list(cls._tools.values())
    
    @classmethod
    def get_default_tools(cls) -> List[Tool]:
        """Get default tool set."""
        return list(cls._tools.values())
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered tools."""
        cls._tools.clear()


class WebSearchTool(Tool):
    """Tool for web search operations."""
    name: str = "web_search"
    description: str = "Search the web for information"
    parameters: Dict[str, Any] = {
        "query": {"type": "string", "required": True},
        "num_results": {"type": "integer", "default": 5},
    }
    
    async def execute(self, **kwargs) -> ToolResult:
        query = kwargs.get("query", "")
        num_results = kwargs.get("num_results", 5)
        
        # Simulated web search
        logger.info(f"Web search: {query}")
        return ToolResult(
            success=True,
            output=[f"Result {i} for: {query}" for i in range(num_results)],
            metadata={"query": query, "num_results": num_results}
        )


class FileOperationsTool(Tool):
    """Tool for file operations."""
    name: str = "file_operations"
    description: str = "Read, write, and manage files"
    parameters: Dict[str, Any] = {
        "operation": {"type": "string", "enum": ["read", "write", "list", "delete"]},
        "path": {"type": "string"},
        "content": {"type": "string", "required": False},
    }
    
    async def execute(self, **kwargs) -> ToolResult:
        operation = kwargs.get("operation")
        path = kwargs.get("path")
        content = kwargs.get("content")
        
        logger.info(f"File operation: {operation} on {path}")
        
        try:
            if operation == "read":
                with open(path, 'r') as f:
                    output = f.read()
            elif operation == "write":
                with open(path, 'w') as f:
                    f.write(content or "")
                output = f"Written to {path}"
            elif operation == "list":
                import os
                output = os.listdir(path)
            elif operation == "delete":
                import os
                os.remove(path)
                output = f"Deleted {path}"
            else:
                return ToolResult(success=False, error=f"Unknown operation: {operation}")
            
            return ToolResult(success=True, output=output)
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class CodeExecutionTool(Tool):
    """Tool for code execution."""
    name: str = "code_execution"
    description: str = "Execute code snippets"
    parameters: Dict[str, Any] = {
        "code": {"type": "string", "required": True},
        "language": {"type": "string", "default": "python"},
    }
    
    async def execute(self, **kwargs) -> ToolResult:
        code = kwargs.get("code", "")
        language = kwargs.get("language", "python")
        
        logger.info(f"Executing {language} code")
        
        # Simulated code execution (in production, use sandboxed execution)
        return ToolResult(
            success=True,
            output=f"Executed {language} code ({len(code)} chars)",
            metadata={"language": language, "code_length": len(code)}
        )


# Register default tools
ToolRegistry.register(WebSearchTool())
ToolRegistry.register(FileOperationsTool())
ToolRegistry.register(CodeExecutionTool())