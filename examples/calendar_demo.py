import os, asyncio
from dotenv import load_dotenv
load_dotenv()

from src.empowering_agents.personalities.fitness_coach import FitnessCoach


async def main():
    user = "calendar_user"
    agent = FitnessCoach(llm_config={})
    # Ask the agent something that triggers scheduling
    print("User: I need a 30-minute workout block this evening. Can you schedule it?")
    ctx = {"schedule_block": {
        "summary": "Workout",
        # Set reasonable ISO times for a demo; change as needed before running
        "start": "2030-01-01T18:00:00+00:00",
        "end": "2030-01-01T18:30:00+00:00",
        "timeZone": os.getenv("GOOGLE_CALENDAR_TIMEZONE", "Europe/London")
    }}
    resp = await agent.interact(user, "Please schedule a workout for me", context=ctx)
    print("Agent:", resp.message)
    print("Actions:", resp.actions)
    print("Note: To actually create events, set GOOGLE_CALENDAR_ENABLED=true, place your client_secret.json, and run OAuth once.")

if __name__ == "__main__":
    asyncio.run(main())
