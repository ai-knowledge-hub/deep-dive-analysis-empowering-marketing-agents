import asyncio
from typing import Dict, Any

from ..integrations import google_calendar as gcal

class ToolRegistry:
    def __init__(self, tools):
        self.tools = set(tools or [])

    async def use_tool(self, name: str, user_id: str, intent: Dict[str, Any], context: Dict[str, Any]) -> Any:
        if name not in self.tools:
            return {"error": f"tool {name} not registered"}
        if name == "calendar":
            return await self._calendar_tool(user_id, intent, context)
        if name == "knowledge_base":
            return await self._kb_tool(user_id, intent, context)
        if name == "external_api":
            return await self._external_api_tool(user_id, intent, context)
        if name == "progress_tracker":
            return {"ok": True}
        if name == "resource_finder":
            return {"resources": ["Intro to Data Analysis (Free)", "Practical Statistics Crash Course"]}
        return {"ok": True}

    async def _calendar_tool(self, user_id, intent, context):
        # Minimal mock: suggest a schedule block
        
enabled = os.getenv("GOOGLE_CALENDAR_ENABLED", "false").lower() == "true"
# If the caller passed an explicit block to create
schedule = (context or {}).get("schedule_block")
if schedule and enabled:
    # Expect ISO datetimes
    summary = schedule.get("summary", "Focus Block")
    start_iso = schedule.get("start")
    end_iso = schedule.get("end")
    tz = schedule.get("timeZone", os.getenv("GOOGLE_CALENDAR_TIMEZONE", "UTC"))
    if start_iso and end_iso:
        created = gcal.create_event(summary, start_iso, end_iso, tz)
        return {"enabled": True, "result": created}
# Otherwise: if enabled, list upcoming and suggest a default
if enabled:
    listing = gcal.list_upcoming_events(max_results=5)
    suggestion = gcal.suggest_block_and_optionally_create(create=False)
    return {"enabled": True, "upcoming": listing, "suggestion": suggestion}
# Fallback if not enabled
return {"enabled": False, "suggested_block": {"day": "tomorrow", "time": "18:00-18:30"}}


    async def _kb_tool(self, user_id, intent, context):
        # Minimal mock "KB"
        query = intent.get("surface_intent", "")
        if "correlation" in query.lower():
            return {"kb": "Correlation ≠ causation; controlled experiments establish causality."}
        return {"kb": "No specific article found; try refining your query."}

    async def _external_api_tool(self, user_id, intent, context):
        # Placeholder for calling out to 3rd party APIs
        await asyncio.sleep(0.05)
        return {"status": "called_external_api", "details": {"service": "example"}}
