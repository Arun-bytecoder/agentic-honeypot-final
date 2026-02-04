import re

def extract_intelligence(text):
    return {
        "upi_ids": re.findall(r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}", text),
        "bank_accounts": re.findall(r"\b\d{9,18}\b", text),
        "urls": re.findall(r"https?://\S+", text)
    }
