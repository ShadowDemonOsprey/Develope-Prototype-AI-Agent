"""
Prototype AI Agent - Main package.
"""
from .agent import Agent, AgentState
from .config import AgentConfig, ToolConfig, ReasoningConfig, AutomationConfig, DEFAULT_CONFIG
from .tools import Tool, ToolRegistry, ToolResult, WebSearchTool, FileOperationsTool, CodeExecutionTool
from .reasoning import ReasoningPipeline, ReasoningResult, ReasoningModule
from .automation import Task, ExecutionMetrics, AutomationStrategy, SequentialStrategy, ParallelStrategy, AdaptiveStrategy

__version__ = "0.1.0"
__all__ = [
    "Agent",
    "AgentState",
    "AgentConfig",
    "ToolConfig",
    "ReasoningConfig",
    "AutomationConfig",
    "DEFAULT_CONFIG",
    "Tool",
    "ToolRegistry",
    "ToolResult",
    "WebSearchTool",
    "FileOperationsTool",
    "CodeExecutionTool",
    "ReasoningPipeline",
    "ReasoningResult",
    "ReasoningModule",
    "Task",
    "ExecutionMetrics",
    "AutomationStrategy",
    "SequentialStrategy",
    "ParallelStrategy",
    "AdaptiveStrategy",
]