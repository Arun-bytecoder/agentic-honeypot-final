from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime
import re
import os
import time

# =========================
# CONFIG
# =========================
API_KEY = os.getenv("API_KEY", "dev_key")  # change this
APP_NAME = "Agentic Honeypot API"

# =========================
# APP INIT
# =========================
app = FastAPI(title=APP_NAME)

# =========================
# IN-MEMORY STORAGE
# =========================
conversation_store: Dict[str, Dict] = {}

# =========================
# REQUEST MODEL
# =========================
class HoneypotRequest(BaseModel):
    conversation_id: str
    message: str
    timestamp: str

# =========================
# RESPONSE MODEL
# =========================
class Engagement(BaseModel):
    turns: int
    duration_seconds: int

class Intelligence(BaseModel):
    upi_ids: List[str]
    bank_accounts: List[str]
    urls: List[str]

class HoneypotResponse(BaseModel):
    scam_detected: bool
    agent_engaged: bool
    conversation_id: str
    engagement: Engagement
    extracted_intelligence: Intelligence
    agent_reply: str

# =========================
# AUTH
# =========================
def verify_api_key(x_api_key: str):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

# =========================
# SCAM DETECTION
# =========================
SCAM_KEYWORDS = [
    "won", "lottery", "urgent", "click", "verify",
    "free", "prize", "account blocked", "reward",
    "payment", "upi", "bank"
]

def is_scam(message: str) -> bool:
    msg = message.lower()
    return any(keyword in msg for keyword in SCAM_KEYWORDS)

# =========================
# AGENT LOGIC
# =========================
AGENT_REPLIES = [
    "Sorry, I didn't understand. Can you explain?",
    "Oh okay, how do I receive the money?",
    "Do I need to send any details?",
    "Can you share the payment link again?",
    "Is this the correct UPI ID?"
]


def agent_reply(turn: int) -> str:
    if turn < len(AGENT_REPLIES):
        return AGENT_REPLIES[turn]
    return "Please guide me, I’m a bit confused."

# =========================
# INTELLIGENCE EXTRACTION
# =========================
def extract_intelligence(text: str):
    return {
        "upi_ids": re.findall(r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}", text),
        "bank_accounts": re.findall(r"\b\d{9,18}\b", text),
        "urls": re.findall(r"https?://\S+", text)
    }

# =========================
# MAIN ENDPOINT
# =========================
@app.post("/honeypot", response_model=HoneypotResponse)
def honeypot_endpoint(
    data: HoneypotRequest,
    x_api_key: str = Header(...)
):
    # ---- AUTH ----
    verify_api_key(x_api_key)

    # ---- INIT MEMORY ----
    if data.conversation_id not in conversation_store:
        conversation_store[data.conversation_id] = {
            "start_time": time.time(),
            "turns": 0,
            "scam_detected": False
        }

    memory = conversation_store[data.conversation_id]
    memory["turns"] += 1

    # ---- SCAM DETECTION ----
    scam = is_scam(data.message)
    if scam:
        memory["scam_detected"] = True

    # ---- AGENT DECISION ----
    agent_engaged = memory["scam_detected"]

    if agent_engaged:
        reply = agent_reply(memory["turns"] - 1)
    else:
        reply = "Thank you for the information."

    # ---- INTELLIGENCE EXTRACTION ----
    intel = extract_intelligence(data.message)

    # ---- ENGAGEMENT METRICS ----
    duration = int(time.time() - memory["start_time"])

    # ---- FINAL RESPONSE ----
    return HoneypotResponse(
        scam_detected=memory["scam_detected"],
        agent_engaged=agent_engaged,
        conversation_id=data.conversation_id,
        engagement=Engagement(
            turns=memory["turns"],
            duration_seconds=duration
        ),
        extracted_intelligence=Intelligence(
            upi_ids=intel["upi_ids"],
            bank_accounts=intel["bank_accounts"],
            urls=intel["urls"]
        ),
        agent_reply=reply
    )
