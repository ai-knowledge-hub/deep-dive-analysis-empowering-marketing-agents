# Architecture

**Core components**
- `EmpoweringAgent`: base class orchestrating memory, planning, tools, and persona style.
- `UserMemorySystem`: summaries, preferences, and recent interactions.
- `GoalTracker`: track user goals and progress (simple in-memory + persistence hook).
- `GoalPlanner` & `ActionPlanner`: turn intents into plans and steps.
- `ToolRegistry`: adapters for external capabilities (calendar, knowledge, APIs).

**Flow**
1. `interact()` loads memory and goals.
2. `_analyze_user_intent()` uses the LLM to get deeper needs (with dummy fallback).
3. `_identify_tools_needed()` selects tools to call.
4. `_build_response_prompt()` composes a persona-aware prompt.
5. LLM generates a structured response (or dummy fallback).
6. Memory and goals are updated and analytics recorded.
