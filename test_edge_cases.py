import asyncio
from src.agent import Agent
from src.tools import ToolRegistry, Tool, ToolResult
from src.config import AgentConfig, ToolConfig

class FailingTool(Tool):
    name: str = "failing_tool"
    description: str = "Tool that always fails"
    parameters: dict = {}
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(success=False, error="Intentional failure")

async def test_edge_cases():
    print("=== Edge Case Tests ===\n")
    
    # Test 1: Custom tool that fails
    print("Test 1: Task with failing tool")
    ToolRegistry.register(FailingTool())
    agent = Agent()
    result = await agent.execute('Use failing tool')
    print(f'  Result: success={result["success"]}, error={result.get("error")}')
    print(f'  Task results: {result["task_results"]}')
    print()
    
    # Test 2: Empty task
    print("Test 2: Empty task description")
    agent2 = Agent()
    result = await agent2.execute('')
    print(f'  Result: success={result["success"]}')
    print()
    
    # Test 3: Config with disabled tools
    print("Test 3: Config with disabled tools")
    config = AgentConfig(
        tools=[
            ToolConfig(name="web_search", enabled=False),
            ToolConfig(name="file_operations", enabled=False),
            ToolConfig(name="code_execution", enabled=False),
        ]
    )
    agent3 = Agent(config=config)
    tools = agent3.get_available_tools()
    print(f'  Available tools: {len(tools)}')
    print()
    
    # Test 4: Check reasoning output structure
    print("Test 4: Reasoning pipeline output structure")
    from src.reasoning import ReasoningPipeline
    pipeline = ReasoningPipeline()
    reasoning_result = await pipeline.run("Test task")
    print(f'  Success: {reasoning_result.success}')
    print(f'  Steps: {len(reasoning_result.steps)}')
    for step in reasoning_result.steps:
        print(f'    - {step.step_type}: {type(step.output)}')
    print(f'  Final output keys: {reasoning_result.final_output.keys() if isinstance(reasoning_result.final_output, dict) else "N/A"}')
    print()
    
    # Test 5: Parallel strategy with dependencies
    print("Test 5: Parallel strategy with dependencies")
    from src.automation import ParallelStrategy, Task
    strategy = ParallelStrategy(max_concurrent=2)
    tasks = [
        Task(id="1", description="Task 1", tools=["web_search"], parameters={"query": "test"}),
        Task(id="2", description="Task 2", tools=["web_search"], parameters={"query": "test2"}, dependencies=["1"]),
        Task(id="3", description="Task 3", tools=["web_search"], parameters={"query": "test3"}, dependencies=["1"]),
    ]
    metrics = await strategy.execute(tasks, ToolRegistry)
    print(f'  Completed: {metrics.completed_tasks}, Failed: {metrics.failed_tasks}')
    for t in tasks:
        print(f'  Task {t.id}: {t.status}')
    print()

asyncio.run(test_edge_cases())