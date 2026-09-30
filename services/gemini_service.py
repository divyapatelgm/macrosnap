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
_SUGGESTION = re.compile(r"<suggestion>(.*?)</suggestion>", re.S)


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
        score = d.get("score", 7)
        try:
            score = max(1, min(10, int(float(score))))
        except Exception:
            score = 7
        meal.update(
            name=str(d.get("name", "Meal")),
            items=[str(i) for i in d.get("items", [])][:8],
            confidence=str(d.get("confidence", "medium")).lower(),
            type=str(d.get("type", "snack")).lower(),
            score=score,
            verdict=str(d.get("verdict", "Logged")).strip() or "Logged",
            emoji=str(d.get("emoji", "🍽️")).strip()[:4] or "🍽️",
        )
        return clean, meal
    except Exception:
        log.warning("Could not parse meal block: %s", m.group(1))
        return clean, None


def split_suggestion(text):
    """Return (clean_text, suggestion_dict_or_None) for the recommend-a-meal flow."""
    m = _SUGGESTION.search(text or "")
    clean = _SUGGESTION.sub("", text or "").strip()
    if not m:
        return clean, None
    try:
        d = json.loads(m.group(1))
        return clean, {"title": str(d.get("title", "Something balanced")),
                       "why": str(d.get("why", "")).strip()}
    except Exception:
        log.warning("Could not parse suggestion block: %s", m.group(1))
        return clean, None


def _is_overloaded(msg):
    return "503" in msg or "unavailable" in msg or "overloaded" in msg


def ask(chat, parts):
    """Send a message, pivoting through config.FALLBACK_MODELS on overload.
    On success the chat is LEFT on whichever model worked, so later messages
    in this session start there instead of repeating models that just failed.
    """
    models_to_try = [chat._model]
    for m in getattr(config, "FALLBACK_MODELS", []):
        if m not in models_to_try:
            models_to_try.append(m)

    text, last = None, None
    for i, model_name in enumerate(models_to_try):
        chat._model = model_name
        try:
            text = chat.send_message(parts).text
            if i > 0:
                log.info("Recovered using fallback model: %s", model_name)
            break
        except Exception as e:
            last = e
            msg = str(e).lower()
            log.warning("Gemini model %s failed: %s", model_name, e)
            if _is_overloaded(msg) and i < len(models_to_try) - 1:
                time.sleep(1.5)
                continue
            break  # non-overload error, or no models left: stop retrying

    if text is None:
        chat._model = models_to_try[0]  # only reset to primary on total failure
        msg = str(last).lower()
        log.error("Gemini request failed on every model tried: %s", last)
        if _is_overloaded(msg):
            raise GeminiError("All AI models are busy right now. Please try again in a minute.")
        if "api key" in msg or "403" in msg or "401" in msg:
            raise GeminiError("MacroSnap can't reach its AI right now (API key problem).")
        if "429" in msg or "quota" in msg:
            raise GeminiError("The AI is busy right now. Give it a minute and try again.")
        if "404" in msg or "not found" in msg:
            raise GeminiError("One of the configured AI models is no longer available.")
        raise GeminiError("Something went wrong analysing that. Please try again.")

    if not text:
        raise GeminiError("I couldn't come up with an answer for that. Try rephrasing.")
    return text
