def parse_avant_apres(value: str) -> str:
    normalized_value = value.lower()
    if normalized_value == "avant":
        return "avant"
    if normalized_value == "a":
        return ""
    if normalized_value in ("apres", "après"):
        return "après"
    raise ValueError(f"Unsupported value '{value}' for avant/après")
