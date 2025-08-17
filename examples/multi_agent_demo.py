import asyncio
from dotenv import load_dotenv
load_dotenv()

from src.empowering_agents.personalities.learning_navigator import LearningNavigator
from src.empowering_agents.personalities.fitness_coach import FitnessCoach

async def main():
    user = "demo_user_multi"
    learn = LearningNavigator(llm_config={})
    fit = FitnessCoach(llm_config={})

    r1 = await learn.interact(user, "I want to transition into data science in 4 months.")
    print("[Learning Navigator]", r1.message)

    r2 = await fit.interact(user, "I sit all day. Can you give me a daily 10-minute routine to keep energy up?")
    print("[Fitness Coach]", r2.message)

if __name__ == "__main__":
    asyncio.run(main())
