from typing import Dict, List, Any
import json
from ..core.agent import EmpoweringAgent

class FitnessCoach(EmpoweringAgent):
    def __init__(self, llm_config: Dict[str, Any]):
        personality_config = {
            "name": "Sam",
            "role": "Fitness Coach",
            "style": "direct, supportive, safety-first",
            "expertise": ["bodyweight training", "habit building"],
            "values": ["consistency", "proper form", "progressive overload"]
        }
        tools = ["calendar", "progress_tracker", "knowledge_base"]
        super().__init__(
            agent_id="fitness_coach_v1",
            personality_config=personality_config,
            llm_config=llm_config,
            tools=tools
        )

    def _get_personality_context(self) -> str:
        return (
            "You are Sam, a pragmatic fitness coach. Prioritize safety and consistency. "
            "Offer 10-20 minute routines when time is short. Adapt plans to constraints. "
            "Be actionable and encouraging."
        )

    def _build_response_prompt(
        self,
        message: str,
        intent: Dict[str, Any],
        user_memory: Dict[str, Any],
        user_goals: List[Any],
        personality_context: str,
        tool_results: Dict[str, Any]
    ) -> str:
        tool_ctx = json.dumps(tool_results, indent=2)
        return f'''
{personality_context}

User says: "{message}"
Intent: {json.dumps(intent)}

Available tool info:
{tool_ctx}

Return JSON:
{{
  "message": "coaching reply",
  "actions": [{{"type":"schedule_workout","details":"..."}]}],
  "goal_updates": [],
  "personalization_learned": {{}}
}}
'''
