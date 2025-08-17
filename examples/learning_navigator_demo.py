import asyncio, os
from dotenv import load_dotenv
load_dotenv()

from src.empowering_agents.personalities.learning_navigator import LearningNavigator

async def main():
    agent = LearningNavigator(llm_config={"temperature": 0.3})
    user = "demo_user_1"
    print("User: Hi! I want to learn data analysis to get a better job. I have about 3 months.")
    r1 = await agent.interact(user, "Hi! I want to learn data analysis to get a better job. I have about 3 months.")
    print("Agent:", r1.message)
    print("Actions:", r1.actions)

    print("\nUser: I'm struggling with correlation vs causation. Can you explain?")
    r2 = await agent.interact(user, "I'm struggling with correlation vs causation. Can you explain?")
    print("Agent:", r2.message)

if __name__ == "__main__":
    asyncio.run(main())
