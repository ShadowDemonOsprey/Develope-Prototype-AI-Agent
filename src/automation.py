"""
Automation strategies for task execution.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from pydantic import BaseModel, Field
from dataclasses import dataclass, field
import asyncio
import time
import logging

logger = logging.getLogger(__name__)


@dataclass
class Task:
    """Represents a task to be executed."""
    id: str
    description: str
    tools: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"
    result: Any = None
    error: Optional[str] = None
    retries: int = 0


@dataclass
class ExecutionMetrics:
    """Metrics for task execution."""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_time: float = 0.0
    average_time: float = 0.0
    efficiency_score: float = 0.0


class AutomationStrategy(ABC):
    """Base class for automation strategies."""
    
    @abstractmethod
    async def execute(self, tasks: List[Task], tool_registry: Any) -> ExecutionMetrics:
        """Execute a list of tasks."""
        pass


class SequentialStrategy(AutomationStrategy):
    """Execute tasks sequentially."""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    async def execute(self, tasks: List[Task], tool_registry: Any) -> ExecutionMetrics:
        metrics = ExecutionMetrics()
        metrics.total_tasks = len(tasks)
        start_time = time.time()
        
        for task in tasks:
            task.status = "running"
            success = await self._execute_task(task, tool_registry)
            
            if success:
                task.status = "completed"
                metrics.completed_tasks += 1
            else:
                task.status = "failed"
                metrics.failed_tasks += 1
        
        metrics.total_time = time.time() - start_time
        metrics.average_time = metrics.total_time / max(metrics.total_tasks, 1)
        metrics.efficiency_score = metrics.completed_tasks / max(metrics.total_tasks, 1)
        
        return metrics
    
    async def _execute_task(self, task: Task, tool_registry: Any) -> bool:
        """Execute a single task with retries."""
        for attempt in range(self.max_retries + 1):
            try:
                if task.tools:
                    tool = tool_registry.get(task.tools[0])
                    if tool:
                        result = await tool.execute(**task.parameters)
                        task.result = result
                        return result.success
                return True
            except Exception as e:
                task.error = str(e)
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay)
                    task.retries += 1
                else:
                    logger.error(f"Task {task.id} failed after {self.max_retries} retries: {e}")
        return False


class ParallelStrategy(AutomationStrategy):
    """Execute tasks in parallel where possible."""
    
    def __init__(self, max_concurrent: int = 5, max_retries: int = 3):
        self.max_concurrent = max_concurrent
        self.max_retries = max_retries
    
    async def execute(self, tasks: List[Task], tool_registry: Any) -> ExecutionMetrics:
        metrics = ExecutionMetrics()
        metrics.total_tasks = len(tasks)
        start_time = time.time()
        
        # Group tasks by dependencies
        ready_tasks = [t for t in tasks if not t.dependencies]
        running_tasks = []
        
        while ready_tasks or running_tasks:
            # Start new tasks up to concurrency limit
            while ready_tasks and len(running_tasks) < self.max_concurrent:
                task = ready_tasks.pop(0)
                task.status = "running"
                running_tasks.append(asyncio.create_task(self._execute_task(task, tool_registry)))
            
            # Wait for at least one task to complete
            if running_tasks:
                done, running_tasks = await asyncio.wait(
                    running_tasks, return_when=asyncio.FIRST_COMPLETED
                )
                
                for task_future in done:
                    task = task_future.result()
                    if task.status == "completed":
                        metrics.completed_tasks += 1
                        # Check for newly ready tasks
                        for t in tasks:
                            if task.id in t.dependencies and t.status == "pending":
                                t.dependencies.remove(task.id)
                                if not t.dependencies:
                                    ready_tasks.append(t)
                    else:
                        metrics.failed_tasks += 1
        
        metrics.total_time = time.time() - start_time
        metrics.average_time = metrics.total_time / max(metrics.total_tasks, 1)
        metrics.efficiency_score = metrics.completed_tasks / max(metrics.total_tasks, 1)
        
        return metrics
    
    async def _execute_task(self, task: Task, tool_registry: Any) -> Task:
        """Execute a single task."""
        for attempt in range(self.max_retries + 1):
            try:
                if task.tools:
                    tool = tool_registry.get(task.tools[0])
                    if tool:
                        result = await tool.execute(**task.parameters)
                        task.result = result
                        task.status = "completed" if result.success else "failed"
                        return task
                task.status = "completed"
                return task
            except Exception as e:
                task.error = str(e)
                if attempt < self.max_retries:
                    await asyncio.sleep(1.0)
                    task.retries += 1
                else:
                    task.status = "failed"
        return task


class AdaptiveStrategy(AutomationStrategy):
    """Adaptive strategy that chooses execution mode based on task characteristics."""
    
    def __init__(self, threshold: int = 3):
        self.threshold = threshold
        self.sequential = SequentialStrategy()
        self.parallel = ParallelStrategy()
    
    async def execute(self, tasks: List[Task], tool_registry: Any) -> ExecutionMetrics:
        # Choose strategy based on task count and dependencies
        has_dependencies = any(t.dependencies for t in tasks)
        
        if len(tasks) <= self.threshold or has_dependencies:
            logger.info("Using sequential strategy")
            return await self.sequential.execute(tasks, tool_registry)
        else:
            logger.info("Using parallel strategy")
            return await self.parallel.execute(tasks, tool_registry)