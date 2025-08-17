import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

from .memory import UserMemorySystem, GoalTracker
from .planning import GoalPlanner, ActionPlanner
from .tools import ToolRegistry
from ..utils.llm_utils import LLMClient

@dataclass
class UserGoal:
    id: str
    description: str
    target_date: str  # ISO string for simplicity
    current_progress: float = 0.0
    milestones: List[str] = None
    context: Dict[str, Any] = None

    def __post_init__(self):
        if self.milestones is None:
            self.milestones = []
        if self.context is None:
            self.context = {}

@dataclass
class AgentResponse:
    message: str
    actions: List[Dict[str, Any]] = None
    goal_updates: List[Dict[str, Any]] = None
    personalization_learned: Dict[str, Any] = None

    def __post_init__(self):
        if self.actions is None:
            self.actions = []
        if self.goal_updates is None:
            self.goal_updates = []
        if self.personalization_learned is None:
            self.personalization_learned = {}

class EmpoweringAgent(ABC):
    def __init__(
        self,
        agent_id: str,
        personality_config: Dict[str, Any],
        llm_config: Dict[str, Any],
        tools: Optional[List[str]] = None
    ):
        self.agent_id = agent_id
        self.personality_config = personality_config
        self.llm_config = llm_config

        self.llm = LLMClient.from_env(llm_config)

        self.memory_system = UserMemorySystem()
        self.goal_tracker = GoalTracker()
        self.goal_planner = GoalPlanner(self.llm)
        self.action_planner = ActionPlanner(self.llm)
        self.tool_registry = ToolRegistry(tools or [])

        self.interaction_count = 0
        self.goals_helped_complete = 0
        self.user_satisfaction_scores: List[float] = []

    async def interact(
        self,
        user_id: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        self.interaction_count += 1

        user_memory = await self.memory_system.load_user_memory(user_id)
        user_goals = await self.goal_tracker.get_active_goals(user_id)

        intent = await self._analyze_user_intent(message, user_memory, context)

        tools_needed = await self._identify_tools_needed(intent)
        tool_results = {}
        for tool_name in tools_needed:
            tool_result = await self.tool_registry.use_tool(
                tool_name, user_id, intent, context or {}
            )
            tool_results[tool_name] = tool_result

        personality_context = self._get_personality_context()
        response_prompt = self._build_response_prompt(
            message, intent, user_memory, user_goals, personality_context, tool_results
        )

        raw_response = await self.llm.generate(response_prompt)

        structured = self._parse_agent_response(raw_response)
        agent_response = AgentResponse(**structured)

        await self._update_user_state(user_id, message, agent_response, user_memory)

        return agent_response

    async def _analyze_user_intent(
        self,
        message: str,
        user_memory: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        prompt = f'''
You are an intent analyzer for empowerment-focused agents.

Message: "{message}"
User Summary: {json.dumps(user_memory.get("summary", {}))}

Return JSON with keys:
- surface_intent
- deeper_needs
- goal_relevance
- empowerment_opportunity
- needs_scheduling (bool)
- needs_data_lookup (bool)
- needs_external_service (bool)
'''
        analysis = await self.llm.generate(prompt)
        try:
            return json.loads(analysis)
        except Exception:
            # Simple fallback
            return {
                "surface_intent": message,
                "deeper_needs": "help user progress toward their goal",
                "goal_relevance": "unknown",
                "empowerment_opportunity": "provide next steps and resources",
                "needs_scheduling": "schedule" in message.lower(),
                "needs_data_lookup": any(k in message.lower() for k in ["what", "how", "resource", "find"]),
                "needs_external_service": False,
            }

    @abstractmethod
    def _get_personality_context(self) -> str:
        ...

    @abstractmethod
    def _build_response_prompt(
        self,
        message: str,
        intent: Dict[str, Any],
        user_memory: Dict[str, Any],
        user_goals: List[UserGoal],
        personality_context: str,
        tool_results: Dict[str, Any]
    ) -> str:
        ...

    def _parse_agent_response(self, response: str) -> Dict[str, Any]:
        try:
            data = json.loads(response)
            if isinstance(data, dict) and "message" in data:
                return data
        except Exception:
            pass
        # Fallback to plain text
        return {
            "message": response,
            "actions": [],
            "goal_updates": [],
            "personalization_learned": {}
        }

    async def _update_user_state(
        self,
        user_id: str,
        user_message: str,
        agent_response: AgentResponse,
        user_memory: Dict[str, Any]
    ):
        await self.memory_system.add_interaction(
            user_id, user_message, agent_response.message
        )
        for gu in agent_response.goal_updates:
            await self.goal_tracker.update_goal_progress(
                user_id, gu.get("goal_id", ""), float(gu.get("progress", 0.0))
            )

    async def _identify_tools_needed(self, intent: Dict[str, Any]) -> List[str]:
        tools = []
        if intent.get("needs_scheduling"):
            tools.append("calendar")
        if intent.get("needs_data_lookup"):
            tools.append("knowledge_base")
        if intent.get("needs_external_service"):
            tools.append("external_api")
        return tools

    def get_empowerment_metrics(self) -> Dict[str, Any]:
        avg_sat = (
            sum(self.user_satisfaction_scores) / len(self.user_satisfaction_scores)
            if self.user_satisfaction_scores else 0.0
        )
        return {
            "total_interactions": self.interaction_count,
            "goals_helped_complete": self.goals_helped_complete,
            "average_satisfaction": avg_sat,
            "empowerment_score": self._calculate_empowerment_score(avg_sat),
        }

    def _calculate_empowerment_score(self, avg_sat: float) -> float:
        if self.interaction_count == 0:
            return 0.0
        goal_completion_rate = self.goals_helped_complete / self.interaction_count
        return (goal_completion_rate * 0.6) + (avg_sat * 0.4)
