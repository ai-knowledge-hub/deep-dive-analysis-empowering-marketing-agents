import os, json, asyncio
from typing import Dict, Any, List

try:
    import dspy  # DSPy for declarative planning
except ImportError:
    dspy = None

DEFAULT_HINTS_PATH = os.getenv("COMPILED_HINTS_PATH", "experiments/.artifacts/compiled_hints.json")

def _load_compiled_hints(path: str = DEFAULT_HINTS_PATH):
    try:
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return None

class GoalPlanner:
    """
    DSPy-backed goal planner.
    Falls back to a simple prompt-based stub if DSPy is unavailable
    or LLM_PROVIDER=dummy.

    If a compiled hints file exists (see experiments/.artifacts/compiled_hints.json),
    it is injected into the context to influence outputs.
    """
    def __init__(self, llm=None):
        self.use_dspy: bool = False
        self.compiled_hints = _load_compiled_hints()
        self._init_dspy()

        if self.use_dspy:
            class PlanGoal(dspy.Signature):
                """Create a SMART learning goal from a user message and context (with optional hints)."""
                user_message: str
                context_json: str  # may include {"compiled_hints": {...}}
                goal_json: str  # JSON with fields: objective, why, timeframe, milestones

            self.plan_goal = dspy.Predict(PlanGoal)

    def _init_dspy(self):
        provider = os.getenv("LLM_PROVIDER", "dummy").lower()
        if dspy is None or provider == "dummy":
            self.use_dspy = False
            return
        if provider == "openai":
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            try:
                dspy.configure(lm=dspy.OpenAI(model=model))
                self.use_dspy = True
            except Exception:
                self.use_dspy = False
        else:
            self.use_dspy = False

    async def plan(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # Inject hints if available
        ctx = dict(context or {})
        if self.compiled_hints:
            ctx["compiled_hints"] = self.compiled_hints

        if self.use_dspy:
            def _run():
                out = self.plan_goal(user_message=user_message, context_json=json.dumps(ctx))
                return out.goal_json
            goal_json = await asyncio.get_event_loop().run_in_executor(None, _run)
            try:
                return json.loads(goal_json)
            except Exception:
                return {"raw": goal_json}

        # Fallback: minimal SMART-like structure
        return {
            "objective": user_message,
            "why": "Progress toward the user's long-term goal",
            "timeframe": ctx.get("timeframe", "90 days"),
            "milestones": ["Define syllabus", "Schedule weekly sessions", "Complete first project"]
        }

class ActionPlanner:
    """
    DSPy-backed action planner that proposes concrete steps.
    Falls back to a simple stub if DSPy is unavailable.

    If a compiled hints file exists, it is injected to influence the outputs.
    """
    def __init__(self, llm=None):
        self.use_dspy: bool = False
        self.compiled_hints = _load_compiled_hints()
        self._init_dspy()

        if self.use_dspy:
            class PlanActions(dspy.Signature):
                """Given a learning goal JSON and hints, return 3 concrete next steps as a JSON list."""
                goal_json: str
                hints_json: str
                steps_json: str  # JSON list of steps

            self.plan_actions = dspy.Predict(PlanActions)

    def _init_dspy(self):
        provider = os.getenv("LLM_PROVIDER", "dummy").lower()
        if dspy is None or provider == "dummy":
            self.use_dspy = False
            return
        if provider == "openai":
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            try:
                dspy.configure(lm=dspy.OpenAI(model=model))
                self.use_dspy = True
            except Exception:
                self.use_dspy = False
        else:
            self.use_dspy = False

    async def steps(self, goal: Dict[str, Any]) -> List[str]:
        if self.use_dspy:
            hints = json.dumps(self.compiled_hints or {})
            def _run():
                out = self.plan_actions(goal_json=json.dumps(goal), hints_json=hints)
                return out.steps_json
            steps_json = await asyncio.get_event_loop().run_in_executor(None, _run)
            try:
                data = json.loads(steps_json)
                if isinstance(data, list):
                    return data
                return [steps_json]
            except Exception:
                return [steps_json]
        # Fallback
        return [
            "Block 25 minutes today for focused practice",
            "Complete a bite-sized lesson related to your goal",
            "Log one takeaway and one question to revisit"
        ]
