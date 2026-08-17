"""
Agent configuration settings.
"""
from typing import Any

import yaml
from pydantic import BaseModel, Field


class ToolConfig(BaseModel):
    """Configuration for a single tool."""
    name: str
    enabled: bool = True
    config: dict[str, Any] = Field(default_factory=dict)


class ReasoningConfig(BaseModel):
    """Configuration for reasoning pipeline."""
    max_steps: int = 10
    timeout_seconds: float = 30.0
    enable_chain_of_thought: bool = True
    enable_planning: bool = True


class AutomationConfig(BaseModel):
    """Configuration for automation strategies."""
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    enable_monitoring: bool = True
    metrics_interval_seconds: float = 5.0


class AgentConfig(BaseModel):
    """Main agent configuration."""
    name: str = "PrototypeAgent"
    version: str = "0.1.0"
    tools: list[ToolConfig] = Field(default_factory=list)
    reasoning: ReasoningConfig = Field(default_factory=ReasoningConfig)
    automation: AutomationConfig = Field(default_factory=AutomationConfig)
    log_level: str = "INFO"
    workspace_dir: str = "./workspace"

    @classmethod
    def from_yaml(cls, path: str) -> "AgentConfig":
        """Load configuration from YAML file."""
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def to_yaml(self, path: str) -> None:
        """Save configuration to YAML file."""
        with open(path, 'w') as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False)


DEFAULT_CONFIG = AgentConfig(
    tools=[
        ToolConfig(name="web_search", enabled=True),
        ToolConfig(name="file_operations", enabled=True),
        ToolConfig(name="code_execution", enabled=True),
    ]
)
