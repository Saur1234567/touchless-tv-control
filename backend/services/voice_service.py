from services.ai_service import process_ai_command
from core.actions import execute_action
from core.logger import log_info, log_error


def process_voice(text: str) -> str:
    if not text or not text.strip():
        return "Nothing heard"
    text = text.strip().lower()
    log_info(f"[VOICE] '{text}'")
    intent = process_ai_command(text)
    log_info(f"[INTENT] {intent}")
    if intent == "UNKNOWN":
        return f"Command not recognized: {text}"
    return execute_action(intent)