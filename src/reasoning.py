"""
Reasoning pipeline components for the agent.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ReasoningStep:
    """A single step in the reasoning process."""
    step_type: str
    input: Any
    output: Any
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ReasoningResult(BaseModel):
    """Result of a reasoning pipeline execution."""
    success: bool
    final_output: Any = None
    steps: List[ReasoningStep] = Field(default_factory=list)
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ReasoningModule(ABC):
    """Base class for reasoning modules."""
    
    @abstractmethod
    async def process(self, input_data: Any, context: Dict[str, Any]) -> Any:
        """Process input and return output."""
        pass


class ChainOfThoughtModule(ReasoningModule):
    """Chain-of-thought reasoning module."""
    
    async def process(self, input_data: Any, context: Dict[str, Any]) -> Any:
        logger.info("Running chain-of-thought reasoning")
        
        # Simulate step-by-step reasoning
        steps = [
            "Analyze the problem",
            "Break down into sub-problems",
            "Identify required tools",
            "Plan execution order",
            "Execute and verify"
        ]
        
        reasoning = "\n".join([f"Step {i+1}: {step}" for i, step in enumerate(steps)])
        
        return {
            "reasoning": reasoning,
            "steps": steps,
            "conclusion": f"Processed: {input_data}"
        }


class PlanningModule(ReasoningModule):
    """Planning module for task decomposition."""
    
    async def process(self, input_data: Any, context: Dict[str, Any]) -> Any:
        logger.info("Running planning module")
        
        # Simulate task planning
        plan = {
            "task": str(input_data),
            "subtasks": [
                {"id": 1, "description": "Understand requirements", "tools": []},
                {"id": 2, "description": "Gather information", "tools": ["web_search"]},
                {"id": 3, "description": "Execute solution", "tools": ["code_execution"]},
                {"id": 4, "description": "Verify results", "tools": []},
            ],
            "estimated_steps": 4
        }
        
        return plan


class ReflectionModule(ReasoningModule):
    """Reflection module for self-evaluation."""
    
    async def process(self, input_data: Any, context: Dict[str, Any]) -> Any:
        logger.info("Running reflection module")
        
        # Simulate reflection on results
        return {
            "evaluation": "Task completed successfully",
            "improvements": ["Optimize tool selection", "Reduce reasoning steps"],
            "confidence": 0.85
        }


class ReasoningPipeline:
    """Pipeline for multi-step reasoning."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.modules: List[ReasoningModule] = []
        self._setup_modules()
    
    def _setup_modules(self) -> None:
        """Initialize reasoning modules based on config."""
        if self.config.get("enable_chain_of_thought", True):
            self.modules.append(ChainOfThoughtModule())
        if self.config.get("enable_planning", True):
            self.modules.append(PlanningModule())
        if self.config.get("enable_reflection", True):
            self.modules.append(ReflectionModule())
    
    async def run(self, input_data: Any, context: Dict[str, Any] = None) -> ReasoningResult:
        """Run the reasoning pipeline."""
        context = context or {}
        steps = []
        current_input = input_data
        
        try:
            for module in self.modules:
                step_start = len(steps)
                output = await module.process(current_input, context)
                
                steps.append(ReasoningStep(
                    step_type=module.__class__.__name__,
                    input=current_input,
                    output=output,
                    metadata={"step_index": step_start}
                ))
                
                current_input = output
            
            return ReasoningResult(
                success=True,
                final_output=current_input,
                steps=steps,
                metadata={"modules_used": [m.__class__.__name__ for m in self.modules]}
            )
        
        except Exception as e:
            logger.error(f"Reasoning pipeline error: {e}")
            return ReasoningResult(
                success=False,
                error=str(e),
                steps=steps
            )