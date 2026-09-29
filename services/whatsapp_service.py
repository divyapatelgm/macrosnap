import json
import logging
import re
import streamlit as st
from twilio.rest import Client

log = logging.getLogger("macrosnap.whatsapp")


def normalize_number(raw):
    """Return +E.164 number or None."""
    n = re.sub(r"[\s\-()]", "", raw or "")
    return n if re.fullmatch(r"\+[1-9]\d{7,14}", n) else None


@st.cache_resource
def _client(sid, token):
    return Client(sid, token)


def clean_text(text):
    if not text:
        return "No nutrition summary available."
    text = " ".join(text.split())
    return text[:1500] + "..." if len(text) > 1500 else text


def send(secrets, to_number, name, summary):
    """Return (ok, user_message)."""
    try:
        _client(secrets["TWILIO_ACCOUNT_SID"], secrets["TWILIO_AUTH_TOKEN"]).messages.create(
            from_=secrets["TWILIO_WHATSAPP_FROM"], to=f"whatsapp:{to_number}",
            content_sid=secrets["TWILIO_CONTENT_SID"],
            content_variables=json.dumps({"1": name, "2": clean_text(summary)}, ensure_ascii=False))
        return True, "Sent"
    except Exception:
        log.exception("Twilio send failed")
        return False, ("We couldn't deliver that. Make sure your number has joined the "
                       "WhatsApp sandbox (it expires after ~72h) and try again.")
