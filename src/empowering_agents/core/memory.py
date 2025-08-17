import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import os

@dataclass
class Interaction:
    timestamp: str
    user_message: str
    agent_response: str
    context: Dict[str, Any]

class UserMemorySystem:
    def __init__(self, storage_dir: str = "./.mem"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self.user_memories = {}

    async def load_user_memory(self, user_id: str) -> Dict[str, Any]:
        if user_id not in self.user_memories:
            path = os.path.join(self.storage_dir, f"{user_id}.json")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    self.user_memories[user_id] = json.load(f)
            else:
                self.user_memories[user_id] = {
                    "user_id": user_id,
                    "created_at": datetime.now().isoformat(),
                    "interactions": [],
                    "preferences": {},
                    "summary": {}
                }
        return self.user_memories[user_id]

    async def add_interaction(
        self,
        user_id: str,
        user_message: str,
        agent_response: str,
        context: Optional[Dict[str, Any]] = None
    ):
        memory = await self.load_user_memory(user_id)
        interaction = Interaction(
            timestamp=datetime.now().isoformat(),
            user_message=user_message,
            agent_response=agent_response,
            context=context or {}
        )
        memory.setdefault("interactions", []).append(asdict(interaction))
        memory["interactions"] = memory["interactions"][-100:]
        await self._update_memory_summary(user_id, memory)
        await self._save_to_storage(user_id, memory)

    async def update_preferences(self, user_id: str, preferences: Dict[str, Any]):
        memory = await self.load_user_memory(user_id)
        memory.setdefault("preferences", {}).update(preferences)
        await self._save_to_storage(user_id, memory)

    async def _update_memory_summary(self, user_id: str, memory: Dict[str, Any]):
        interactions = memory.get("interactions", [])
        last10 = interactions[-10:]
        all_text = " ".join(i["user_message"] for i in last10)
        topics = []
        low = all_text.lower()
        if any(k in low for k in ["fitness", "workout", "gym"]):
            topics.append("fitness")
        if any(k in low for k in ["learn", "study", "course"]):
            topics.append("learning")
        if any(k in low for k in ["money", "budget", "finance"]):
            topics.append("finance")
        avg_len = (sum(len(i["user_message"]) for i in last10)/len(last10)) if last10 else 0
        memory["summary"] = {
            "interaction_count": len(interactions),
            "last_interaction": last10[-1]["timestamp"] if last10 else None,
            "common_topics": topics,
            "user_style": {
                "communication_style": "detailed" if avg_len > 50 else "concise"
            }
        }

    async def _save_to_storage(self, user_id: str, memory: Dict[str, Any]):
        self.user_memories[user_id] = memory
        path = os.path.join(self.storage_dir, f"{user_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2)

class GoalTracker:
    def __init__(self):
        self.user_goals = {}

    async def add_goal(self, user_id: str, goal: Dict[str, Any]):
        self.user_goals.setdefault(user_id, []).append(goal)

    async def update_goal_progress(self, user_id: str, goal_id: str, progress: float):
        for g in self.user_goals.get(user_id, []):
            if g.get("id") == goal_id:
                g["current_progress"] = progress

    async def get_active_goals(self, user_id: str) -> List[Dict[str, Any]]:
        return [g for g in self.user_goals.get(user_id, []) if g.get("current_progress", 0.0) < 1.0]

    async def get_completed_goals(self, user_id: str) -> List[Dict[str, Any]]:
        return [g for g in self.user_goals.get(user_id, []) if g.get("current_progress", 0.0) >= 1.0]
