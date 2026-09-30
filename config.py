import logging
import streamlit as st

logging.basicConfig(level=logging.INFO)

# Primary model, tried first.
MODEL_NAME = "gemini-3.5-flash"

# Tried in order if the primary is overloaded (503) or unavailable.
# "-latest" aliases route to whatever Google currently has best provisioned,
# so they're a good last resort even if every named model is under load.
FALLBACK_MODELS = [
    "gemini-2.5-flash",
    "gemini-flash-latest",
    "gemini-3.5-flash-lite",
    "gemini-flash-lite-latest",
]

# A rough default goal, used only if the person skips goal-setting at onboarding.
DEFAULT_GOAL = {"calories": 2000, "protein": 100, "carbs": 250, "fat": 65}

# calories -> macro presets (protein/carbs/fat %), used to turn a single
# calorie target into grams at onboarding. Rough starting points, not medical advice.
GOAL_PRESETS = {
    "Lose weight": {"calories": 1600, "split": (0.35, 0.35, 0.30)},
    "Maintain": {"calories": 2000, "split": (0.30, 0.40, 0.30)},
    "Build muscle": {"calories": 2400, "split": (0.35, 0.40, 0.25)},
}

KEYS = ["GEMINI_API_KEY", "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN",
        "TWILIO_WHATSAPP_FROM", "TWILIO_CONTENT_SID"]


def goal_from_calories(calories, split=(0.30, 0.40, 0.30)):
    """Turn a calorie target into a goals dict using a protein/carbs/fat % split."""
    p, c, f = split
    return {
        "calories": int(calories),
        "protein": round(calories * p / 4),
        "carbs": round(calories * c / 4),
        "fat": round(calories * f / 9),
    }


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
