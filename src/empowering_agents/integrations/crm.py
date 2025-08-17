# Minimal CRM stub: write contacts to a local JSON store
import json, os
CRM_FILE = "./crm.json"

def upsert_contact(email: str, fields: dict):
    data = {}
    if os.path.exists(CRM_FILE):
        with open(CRM_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    data[email] = {**data.get(email, {}), **fields}
    with open(CRM_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return {"ok": True}
