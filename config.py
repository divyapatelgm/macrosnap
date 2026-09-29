import logging
import streamlit as st

logging.basicConfig(level=logging.INFO)
MODEL_NAME = "gemini-3.5-flash"
FALLBACK_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.7-flash",
]
KEYS = ["GEMINI_API_KEY", "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN",
        "TWILIO_WHATSAPP_FROM", "TWILIO_CONTENT_SID"]


def load_secrets():
    """Return (secrets dict, list of missing key names)."""
    out, missing = {}, []
    for k in KEYS:
        try:
            v = str(st.secrets[k]).strip()
        except Exception:
            v = ""
        if not v or v.startswith("your-"):
            missing.append(k)
        out[k] = v
    return out, missing
