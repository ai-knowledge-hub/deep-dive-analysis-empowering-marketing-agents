import asyncio
from src.empowering_agents.personalities.fitness_coach import FitnessCoach

def test_fitness_coach_runs():
    async def run():
        agent = FitnessCoach(llm_config={})
        r = await agent.interact("u1", "I only have 10 minutes.")
        assert isinstance(r.message, str)
    asyncio.run(run())
