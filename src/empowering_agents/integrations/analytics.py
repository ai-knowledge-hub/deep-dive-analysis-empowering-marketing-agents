import os, json
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

LOG_PATH = os.getenv("ANALYTICS_LOG", "./analytics_events.jsonl")

def record_event(event_type: str, data: Dict[str, Any]):
    os.makedirs(os.path.dirname(LOG_PATH) or ".", exist_ok=True)
    payload = {
        "ts": datetime.now().isoformat(),
        "type": event_type,
        "data": data
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")
