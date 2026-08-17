import asyncio
from src.agent import Agent

async def test():
    agent = Agent()
    
    result = await agent.execute('Test task 1')
    print(f'Task 1: {result["success"]}, efficiency: {result["metrics"]["efficiency"]:.2%}')
    
    result = await agent.execute('Test task 2')
    print(f'Task 2: {result["success"]}, efficiency: {result["metrics"]["efficiency"]:.2%}')
    
    results = await agent.execute_batch(['Batch task 1', 'Batch task 2', 'Batch task 3'])
    print(f'Batch: {len(results)} tasks, all success: {all(r["success"] for r in results)}')
    
    state = agent.get_state()
    print(f'State: completed={state.completed_tasks}, failed={state.failed_tasks}, efficiency={state.total_efficiency:.2%}')

asyncio.run(test())