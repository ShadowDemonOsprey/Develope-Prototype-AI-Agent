"""
Prototype AI Agent - Main package.
"""
from .agent import Agent, AgentState
from .automation import (
    AdaptiveStrategy,
    AutomationStrategy,
    ExecutionMetrics,
    ParallelStrategy,
    SequentialStrategy,
    Task,
)
from .config import DEFAULT_CONFIG, AgentConfig, AutomationConfig, ReasoningConfig, ToolConfig
from .reasoning import ReasoningModule, ReasoningPipeline, ReasoningResult
from .tools import (
    CodeExecutionTool,
    FileOperationsTool,
    Tool,
    ToolRegistry,
    ToolResult,
    WebSearchTool,
)

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
