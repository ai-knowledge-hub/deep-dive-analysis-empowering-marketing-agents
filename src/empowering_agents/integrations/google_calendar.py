import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

# Google API
try:
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
except Exception:  # libs not installed or environment without Google packages
    build = None
    InstalledAppFlow = None
    Request = None
    Credentials = None

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def _expand_user_path(p: str) -> str:
    return os.path.expanduser(os.path.expandvars(p)) if p else p

def _get_creds() -> Optional["Credentials"]:
    token_path = _expand_user_path(os.getenv("GOOGLE_TOKEN_PATH", "~/.empowering_agents/google_token.json"))
    client_secrets = os.getenv("GOOGLE_CLIENT_SECRETS", "./client_secret.json")
    client_secrets = _expand_user_path(client_secrets)

    creds = None
    if Credentials and os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # Refresh or run flow
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception:
            creds = None
    if not creds:
        # No stored token: run installed-app flow if secrets present
        if not (InstalledAppFlow and os.path.exists(client_secrets)):
            return None
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets, SCOPES)
        creds = flow.run_local_server(port=0)
        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, "w", encoding="utf-8") as token:
            token.write(creds.to_json())
    return creds

def _get_service():
    if build is None:
        return None
    creds = _get_creds()
    if not creds:
        return None
    try:
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        return service
    except Exception:
        return None

def list_upcoming_events(max_results: int = 5) -> Dict[str, Any]:
    service = _get_service()
    if not service:
        return {"enabled": False, "reason": "Calendar not configured. Provide GOOGLE_CLIENT_SECRETS and run OAuth."}
    now = datetime.now().isoformat() + "Z"
    events_result = service.events().list(
        calendarId="primary", timeMin=now, maxResults=max_results, singleEvents=True, orderBy="startTime"
    ).execute()
    events = events_result.get("items", [])
    # Return a compact summary
    def _fmt(e):
        start = e.get("start", {}).get("dateTime") or e.get("start", {}).get("date")
        end = e.get("end", {}).get("dateTime") or e.get("end", {}).get("date")
        return {
            "id": e.get("id"),
            "summary": e.get("summary"),
            "start": start,
            "end": end,
            "htmlLink": e.get("htmlLink"),
        }
    return {"enabled": True, "events": [_fmt(e) for e in events]}

def create_event(summary: str, start_iso: str, end_iso: str, timezone_str: Optional[str] = None) -> Dict[str, Any]:
    service = _get_service()
    if not service:
        return {"enabled": False, "reason": "Calendar not configured. Provide GOOGLE_CLIENT_SECRETS and run OAuth."}
    tz = timezone_str or os.getenv("GOOGLE_CALENDAR_TIMEZONE", "UTC")
    body = {
        "summary": summary,
        "start": {"dateTime": start_iso, "timeZone": tz},
        "end": {"dateTime": end_iso, "timeZone": tz},
    }
    try:
        event = service.events().insert(calendarId="primary", body=body).execute()
        return {
            "enabled": True,
            "event": {
                "id": event.get("id"),
                "summary": event.get("summary"),
                "htmlLink": event.get("htmlLink"),
                "start": event.get("start"),
                "end": event.get("end"),
            },
        }
    except Exception as e:
        return {"enabled": False, "reason": f"Insert failed: {e}"}

def suggest_block_and_optionally_create(summary: str = "Focus Block", minutes: int = 30, create: bool = False) -> Dict[str, Any]:
    tz = os.getenv("GOOGLE_CALENDAR_TIMEZONE", "UTC")
    now = datetime.now(timezone.utc)
    start = now + timedelta(minutes=30)  # suggest starting in ~30 minutes
    end = start + timedelta(minutes=minutes)
    start_iso = start.replace(microsecond=0).isoformat()
    end_iso = end.replace(microsecond=0).isoformat()
    suggestion = {"summary": summary, "start": start_iso, "end": end_iso, "timeZone": tz}

    enabled = os.getenv("GOOGLE_CALENDAR_ENABLED", "false").lower() == "true"
    if create and enabled:
        res = create_event(summary, start_iso, end_iso, tz)
        return {"suggestion": suggestion, "created": res}
    return {"suggestion": suggestion, "created": None}
