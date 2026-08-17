"""
Main agent implementation integrating tools, reasoning, and automation.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import asyncio
import logging
import uuid

from .config import AgentConfig, DEFAULT_CONFIG
from .tools import ToolRegistry, Tool
from .reasoning import ReasoningPipeline, ReasoningResult
from .automation import (
    AutomationStrategy, SequentialStrategy, ParallelStrategy, 
    AdaptiveStrategy, Task, ExecutionMetrics
)

logger = logging.getLogger(__name__)


class AgentState(BaseModel):
    """Current state of the agent."""
    status: str = "idle"
    current_task: Optional[str] = None
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_efficiency: float = 0.0


class Agent:
    """Main AI agent class integrating all components."""
    
    def __init__(self, config: AgentConfig = None, tools: List[Tool] = None):
        self.config = config or DEFAULT_CONFIG
        self.state = AgentState()
        self.reasoning_pipeline = ReasoningPipeline({
            "enable_chain_of_thought": self.config.reasoning.enable_chain_of_thought,
            "enable_planning": self.config.reasoning.enable_planning,
            "enable_reflection": True,
        })
        
        # Register tools
        if tools:
            for tool in tools:
                ToolRegistry.register(tool)
        else:
            for tool_config in self.config.tools:
                if tool_config.enabled:
                    # Tools are already registered by default
                    pass
        
        # Initialize automation strategy
        self.automation_strategy = self._create_automation_strategy()
        
        logger.info(f"Agent '{self.config.name}' v{self.config.version} initialized")
    
    def _create_automation_strategy(self) -> AutomationStrategy:
        """Create automation strategy based on config."""
        return AdaptiveStrategy()
    
    async def execute(self, task_description: str, **kwargs) -> Dict[str, Any]:
        """Execute a high-level task."""
        self.state.status = "running"
        self.state.current_task = task_description
        
        task_id = str(uuid.uuid4())[:8]
        logger.info(f"Starting task {task_id}: {task_description}")
        
        try:
            # Step 1: Reasoning - analyze and plan
            reasoning_result = await self.reasoning_pipeline.run(
                task_description,
                context={"config": self.config.model_dump()}
            )
            
            if not reasoning_result.success:
                return {
                    "success": False,
                    "error": reasoning_result.error,
                    "task_id": task_id
                }
            
            # Step 2: Create tasks from plan
            tasks = self._create_tasks_from_plan(reasoning_result.final_output, task_id)
            
            # Step 3: Execute tasks via automation
            metrics = await self.automation_strategy.execute(tasks, ToolRegistry)
            
            # Step 4: Update state and return results
            self.state.completed_tasks += metrics.completed_tasks
            self.state.failed_tasks += metrics.failed_tasks
            self.state.total_efficiency = (
                self.state.completed_tasks / 
                max(self.state.completed_tasks + self.state.failed_tasks, 1)
            )
            self.state.status = "idle"
            self.state.current_task = None
            
            return {
                "success": metrics.failed_tasks == 0,
                "task_id": task_id,
                "reasoning": reasoning_result.final_output,
                "metrics": {
                    "total_tasks": metrics.total_tasks,
                    "completed": metrics.completed_tasks,
                    "failed": metrics.failed_tasks,
                    "efficiency": metrics.efficiency_score,
                    "total_time": metrics.total_time,
                },
                "task_results": [
                    {
                        "id": t.id,
                        "description": t.description,
                        "status": t.status,
                        "result": t.result.output if t.result else None,
                        "error": t.error
                    }
                    for t in tasks
                ]
            }
            
        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            self.state.status = "error"
            return {
                "success": False,
                "error": str(e),
                "task_id": task_id
            }
    
    def _create_tasks_from_plan(self, plan: Any, parent_id: str) -> List[Task]:
        """Create executable tasks from reasoning plan."""
        tasks = []
        
        if isinstance(plan, dict) and "subtasks" in plan:
            for i, subtask in enumerate(plan["subtasks"]):
                task = Task(
                    id=f"{parent_id}-{i+1}",
                    description=subtask.get("description", ""),
                    tools=subtask.get("tools", []),
                    parameters=subtask.get("parameters", {}),
                    dependencies=subtask.get("dependencies", [])
                )
                tasks.append(task)
        else:
            # Single task fallback
            tasks.append(Task(
                id=f"{parent_id}-1",
                description=str(plan),
                tools=["code_execution"],
                parameters={"code": f"# Process: {plan}", "language": "python"}
            ))
        
        return tasks
    
    def get_state(self) -> AgentState:
        """Get current agent state."""
        return self.state
    
    def get_available_tools(self) -> List[Tool]:
        """Get list of available tools."""
        return ToolRegistry.list_tools()
    
    async def execute_batch(self, tasks: List[str]) -> List[Dict[str, Any]]:
        """Execute multiple tasks in batch."""
        results = []
        for task_desc in tasks:
            result = await self.execute(task_desc)
            results.append(result)
        return results


async def main():
    """Example usage."""
    logging.basicConfig(level=logging.INFO)
    
    agent = Agent()
    
    # Example task
    result = await agent.execute(
        "Research and implement a solution for optimizing task scheduling"
    )
    
    print(f"Success: {result['success']}")
    print(f"Efficiency: {result['metrics']['efficiency']:.2%}")
    print(f"Tasks completed: {result['metrics']['completed']}/{result['metrics']['total_tasks']}")


if __name__ == "__main__":
    asyncio.run(main())