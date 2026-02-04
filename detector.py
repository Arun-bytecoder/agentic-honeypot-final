SCAM_KEYWORDS = [
  "won", "lottery", "urgent", "click", "verify",
  "free", "prize", "account blocked"
]

def is_scam(message: str) -> bool:
    message = message.lower()
    return any(word in message for word in SCAM_KEYWORDS)
