import asyncio
from src.empowering_agents.personalities.learning_navigator import LearningNavigator

def test_learning_navigator_runs():
    async def run():
        agent = LearningNavigator(llm_config={})
        r = await agent.interact("test_user", "Help me learn SQL in 2 months.")
        assert isinstance(r.message, str)
    asyncio.run(run())
