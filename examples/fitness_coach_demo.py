import asyncio, os
from dotenv import load_dotenv
load_dotenv()

from src.empowering_agents.personalities.fitness_coach import FitnessCoach

async def main():
    agent = FitnessCoach(llm_config={"temperature": 0.2})
    user = "demo_user_2"
    print("User: I only have 15 minutes a day. What workout should I do?")
    r1 = await agent.interact(user, "I only have 15 minutes a day. What workout should I do?")
    print("Coach:", r1.message)
    print("Actions:", r1.actions)

if __name__ == "__main__":
    asyncio.run(main())
