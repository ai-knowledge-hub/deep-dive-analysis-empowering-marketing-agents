# Minimal notifications stub
def send_notification(user_id: str, message: str):
    print(f"[notify:{user_id}] {message}")
    return {"ok": True}
