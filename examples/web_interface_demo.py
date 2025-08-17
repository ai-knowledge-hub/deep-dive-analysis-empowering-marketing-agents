from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
from src.empowering_agents.personalities.learning_navigator import LearningNavigator
from src.empowering_agents.personalities.fitness_coach import FitnessCoach

app = FastAPI(title="Empowering Agents API")

# instantiate once (simple demo)
learning_agent = LearningNavigator(llm_config={"temperature": 0.3})
fitness_agent = FitnessCoach(llm_config={"temperature": 0.2})

class ChatRequest(BaseModel):
    user_id: str
    message: str
    persona: str = "learning"  # or 'fitness'

@app.post("/chat")
async def chat(req: ChatRequest):
    agent = learning_agent if req.persona == "learning" else fitness_agent
    resp = await agent.interact(req.user_id, req.message)
    return {
        "message": resp.message,
        "actions": resp.actions,
        "goal_updates": resp.goal_updates,
        "personalization_learned": resp.personalization_learned,
    }

@app.get("/healthz")
def healthz():
    return {"ok": True}
