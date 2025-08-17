from typing import Dict, List, Any
import json
from ..core.agent import EmpoweringAgent, UserGoal

class LearningNavigator(EmpoweringAgent):
    def __init__(self, llm_config: Dict[str, Any]):
        personality_config = {
            "name": "Alex",
            "role": "Learning Navigator",
            "style": "encouraging, knowledgeable, adaptive",
            "expertise": ["education", "skill development", "career growth"],
            "values": ["lifelong learning", "practical application", "individual growth"]
        }
        tools = ["knowledge_base", "calendar", "progress_tracker", "resource_finder"]
        super().__init__(
            agent_id="learning_navigator_v1",
            personality_config=personality_config,
            llm_config=llm_config,
            tools=tools
        )

    def _get_personality_context(self) -> str:
        return (
            "You are Alex, a Learning Navigator AI. Focus on helping users achieve learning goals. "
            "Be clear, encouraging, and practical. Recommend free resources when useful. "
            "Celebrate small wins and propose next steps."
        )

    def _build_response_prompt(
        self,
        message: str,
        intent: Dict[str, Any],
        user_memory: Dict[str, Any],
        user_goals: List[UserGoal],
        personality_context: str,
        tool_results: Dict[str, Any]
    ) -> str:
        goals_ctx = ""
        if user_goals:
            goals_ctx = "Active goals:\\n" + "\\n".join(
                f"- {g.get('description','')} ({int(g.get('current_progress',0.0)*100)}%)"
                for g in user_goals
            )

        mem = user_memory.get("summary", {})
        tool_ctx = json.dumps(tool_results, indent=2)

        return f'''
{personality_context}

User style: {mem.get("user_style",{})}
Common topics: {mem.get("common_topics",[])}
{goals_ctx}

Intent:
{json.dumps(intent, indent=2)}

User says: "{message}"

Return JSON with keys:
- "message": a helpful reply
- "actions": list of suggested actions
- "goal_updates": optional updates (goal_id, progress)
- "personalization_learned": new prefs
'''
