import json
import logging
import re
import time
import streamlit as st
import config
from google import genai
from google.genai import types
from prompts import SYSTEM_PROMPT

log = logging.getLogger("macrosnap.gemini")
_MEAL = re.compile(r"<meal>(.*?)</meal>", re.S)


class GeminiError(Exception):
    """Carries a user-friendly message."""


@st.cache_resource
def get_client(api_key):
    return genai.Client(api_key=api_key)


def new_chat(api_key, model):
    return get_client(api_key).chats.create(
        model=model, config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT))


def image_part(data, mime):
    return types.Part.from_bytes(data=data, mime_type=mime)


def split_meal(text):
    """Return (clean_text, meal_dict_or_None)."""
    m = _MEAL.search(text or "")
    clean = _MEAL.sub("", text or "").strip()
    if not m:
        return clean, None
    try:
        d = json.loads(m.group(1))
        meal = {k: int(float(d.get(k, 0))) for k in ("calories", "protein", "carbs", "fat")}
        meal.update(name=str(d.get("name", "Meal")), items=[str(i) for i in d.get("items", [])][:8],
                    confidence=str(d.get("confidence", "medium")).lower(),
                    type=str(d.get("type", "snack")).lower())
        return clean, meal
    except Exception:
        log.warning("Could not parse meal block: %s", m.group(1))
        return clean, None


# def ask(chat, parts):
#     try:
#         text = chat.send_message(parts).text
#     except Exception as e:
#         log.exception("Gemini request failed")
#         msg = str(e).lower()
#         if "api key" in msg or "permission" in msg or "401" in msg or "403" in msg:
#             raise GeminiError("MacroSnap can't reach its AI right now (API key problem).")
#         if "429" in msg or "quota" in msg:
#             raise GeminiError("The AI is busy right now. Give it a minute and try again.")
#         raise GeminiError("Something went wrong analysing that. Please try again.")
#     if not text:
#         raise GeminiError("I couldn't come up with an answer for that. Try rephrasing.")
#     return text

def ask(chat, parts):
    text, last = None, None
    
    models_to_try = [chat._model]
    if hasattr(config, 'FALLBACK_MODELS'):
        for m in config.FALLBACK_MODELS:
            if m not in models_to_try:
                models_to_try.append(m)

    original_model = chat._model

    for model_name in models_to_try:
        chat._model = model_name
        try:
            text = chat.send_message(parts).text
            break
        except Exception as e:
            last = e
            msg = str(e).lower()
            log.warning("Gemini model %s failed: %s", model_name, e)
            if "503" in msg or "unavailable" in msg or "overloaded" in msg:
                # Give it a tiny bit of breathing room before trying the next model
                time.sleep(1)
                continue
            # If it's another kind of error (like 400 or auth), don't try fallback models
            break

    chat._model = original_model

    if text is None:
        msg = str(last).lower()
        log.error("Gemini request failed: %s", last)
        if "503" in msg or "unavailable" in msg:
            raise GeminiError("The AI is very busy right now. Please try again in a minute.")
        if "api key" in msg or "403" in msg or "401" in msg:
            raise GeminiError("MacroSnap can't reach its AI right now (API key problem).")
        if "429" in msg or "quota" in msg:
            raise GeminiError("The AI is busy right now. Give it a minute and try again.")
        raise GeminiError("Something went wrong analysing that. Please try again.")
    if not text:
        raise GeminiError("I couldn't come up with an answer for that. Try rephrasing.")
    return text
