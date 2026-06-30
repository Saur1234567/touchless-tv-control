import datetime


def normalize_text(text: str) -> str:
    if not text:
        return ""
    return text.strip().lower()


def get_timestamp() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def validate_request(data: dict, key: str) -> tuple[bool, str | None]:
    if key not in data:
        return False, f"'{key}' missing from request"
    return True, None