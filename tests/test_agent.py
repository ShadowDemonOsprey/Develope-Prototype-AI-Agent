"""
Tests for the AI agent prototype.
"""
import pytest
import asyncio
from src.agent import Agent
from src.config import AgentConfig, DEFAULT_CONFIG
from src.tools import ToolRegistry, WebSearchTool, FileOperationsTool, CodeExecutionTool
from src.reasoning import ReasoningPipeline, ChainOfThoughtModule, PlanningModule
from src.automation import SequentialStrategy, ParallelStrategy, AdaptiveStrategy, Task


class TestConfig:
    """Test configuration loading."""
    
    def test_default_config(self):
        config = DEFAULT_CONFIG
        assert config.name == "PrototypeAgent"
        assert config.version == "0.1.0"
        assert len(config.tools) == 3
    
    def test_config_from_yaml(self, tmp_path):
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
name: "TestAgent"
version: "1.0.0"
tools:
  - name: "test_tool"
    enabled: true
reasoning:
  max_steps: 5
automation:
  max_retries: 2
""")
        config = AgentConfig.from_yaml(str(config_file))
        assert config.name == "TestAgent"
        assert config.version == "1.0.0"
        assert config.reasoning.max_steps == 5


class TestTools:
    """Test tool registry and implementations."""
    
    def setup_method(self):
        ToolRegistry.clear()
    
    def test_tool_registration(self):
        tool = WebSearchTool()
        ToolRegistry.register(tool)
        assert ToolRegistry.get("web_search") == tool
    
    def test_list_tools(self):
        ToolRegistry.register(WebSearchTool())
        ToolRegistry.register(FileOperationsTool())
        tools = ToolRegistry.list_tools()
        assert len(tools) == 2
    
    @pytest.mark.asyncio
    async def test_web_search_tool(self):
        tool = WebSearchTool()
        result = await tool.execute(query="test query", num_results=3)
        assert result.success
        assert len(result.output) == 3
    
    @pytest.mark.asyncio
    async def test_file_operations_tool(self, tmp_path):
        tool = FileOperationsTool()
        test_file = tmp_path / "test.txt"
        
        # Write
        result = await tool.execute(operation="write", path=str(test_file), content="Hello")
        assert result.success
        
        # Read
        result = await tool.execute(operation="read", path=str(test_file))
        assert result.success
        assert result.output == "Hello"
    
    @pytest.mark.asyncio
    async def test_code_execution_tool(self):
        tool = CodeExecutionTool()
        result = await tool.execute(code="print('hello')", language="python")
        assert result.success


class TestReasoning:
    """Test reasoning pipeline."""
    
    @pytest.mark.asyncio
    async def test_chain_of_thought(self):
        module = ChainOfThoughtModule()
        result = await module.process("test task", {})
        assert "reasoning" in result
        assert "steps" in result
    
    @pytest.mark.asyncio
    async def test_planning_module(self):
        module = PlanningModule()
        result = await module.process("test task", {})
        assert "subtasks" in result
        assert len(result["subtasks"]) > 0
    
    @pytest.mark.asyncio
    async def test_reasoning_pipeline(self):
        pipeline = ReasoningPipeline({
            "enable_chain_of_thought": True,
            "enable_planning": True,
        })
        result = await pipeline.run("test task", {})
        assert result.success
        assert len(result.steps) >= 2


class TestAutomation:
    """Test automation strategies."""
    
    @pytest.mark.asyncio
    async def test_sequential_strategy(self):
        strategy = SequentialStrategy(max_retries=1)
        tasks = [
            Task(id="1", description="Task 1", tools=["web_search"], parameters={"query": "test"}),
            Task(id="2", description="Task 2", tools=["web_search"], parameters={"query": "test2"}),
        ]
        metrics = await strategy.execute(tasks, ToolRegistry)
        assert metrics.total_tasks == 2
        assert metrics.completed_tasks == 2
    
    @pytest.mark.asyncio
    async def test_parallel_strategy(self):
        strategy = ParallelStrategy(max_concurrent=2, max_retries=1)
        tasks = [
            Task(id="1", description="Task 1", tools=["web_search"], parameters={"query": "test"}),
            Task(id="2", description="Task 2", tools=["web_search"], parameters={"query": "test2"}),
        ]
        metrics = await strategy.execute(tasks, ToolRegistry)
        assert metrics.total_tasks == 2
        assert metrics.completed_tasks == 2
    
    @pytest.mark.asyncio
    async def test_adaptive_strategy(self):
        strategy = AdaptiveStrategy()
        tasks = [
            Task(id="1", description="Task 1", tools=["web_search"], parameters={"query": "test"}),
            Task(id="2", description="Task 2", tools=["web_search"], parameters={"query": "test2"}),
            Task(id="3", description="Task 3", tools=["web_search"], parameters={"query": "test3"}),
        ]
        metrics = await strategy.execute(tasks, ToolRegistry)
        assert metrics.total_tasks == 3


class TestAgent:
    """Test main agent."""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        agent = Agent()
        assert agent.config.name == "PrototypeAgent"
        assert len(agent.get_available_tools()) >= 3
    
    @pytest.mark.asyncio
    async def test_agent_execute(self):
        agent = Agent()
        result = await agent.execute("Simple test task")
        assert "success" in result
        assert "task_id" in result
        assert "metrics" in result
    
    @pytest.mark.asyncio
    async def test_agent_state(self):
        agent = Agent()
        initial_state = agent.get_state()
        assert initial_state.status == "idle"
        assert initial_state.completed_tasks == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])