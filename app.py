import io
import logging
import streamlit as st
from PIL import Image

import config
from prompts import DEFAULT_PHOTO_PROMPT, SUMMARY_REQUEST_PROMPT
from services import gemini_service as gem
from services import whatsapp_service as wa
from ui import styles, views

log = logging.getLogger("macrosnap")
st.set_page_config(page_title="MacroSnap", page_icon="🥗", layout="wide")
styles.inject()

secrets, missing = config.load_secrets()
if missing:
    st.markdown(views.BRAND, unsafe_allow_html=True)
    st.error("MacroSnap isn't configured yet. Missing settings: " + ", ".join(missing) +
             ". Copy .streamlit/secrets.toml.example to .streamlit/secrets.toml and fill it in.")
    st.stop()

ss = st.session_state


def start(name, number):
    clean = wa.normalize_number(number)
    if not name.strip():
        st.warning("Please enter your name.")
    elif not clean:
        st.warning("Enter your WhatsApp number with country code, e.g. +919876543210.")
    else:
        try:
            ss.chat = gem.new_chat(secrets["GEMINI_API_KEY"], config.MODEL_NAME)
        except Exception:
            log.exception("Could not start chat")
            st.error("We couldn't start the AI session. Check your Gemini key and try again.")
            return
        ss.name, ss.number, ss.messages, ss.pending, ss.onboarded = name.strip(), clean, [], None, True
        st.rerun()


if "onboarded" not in ss:
    views.render_onboarding(start)
    st.stop()


def queue(text=None, photo=None, mime=None):
    if photo is not None:
        ss.messages.append({"role": "user", "kind": "image", "content": photo})
    if text:
        ss.messages.append({"role": "user", "kind": "text", "content": text})
    ss.pending = (text, photo, mime)
    st.rerun()


def valid_image(data):
    try:
        if len(data) > 8 * 1024 * 1024:
            return False
        Image.open(io.BytesIO(data)).verify()
        return True
    except Exception:
        return False


def process_pending():
    text, photo, mime = ss.pending
    ss.pending = None
    parts = []
    if photo is not None:
        parts.append(gem.image_part(photo, mime))
    parts.append(text or DEFAULT_PHOTO_PROMPT)
    slot = st.empty()
    slot.markdown(views.thinking("Analyzing your meal..." if photo else "Estimating nutrition..."),
                  unsafe_allow_html=True)
    try:
        clean, meal = gem.split_meal(gem.ask(ss.chat, parts))
        ss.messages.append({"role": "assistant", "kind": "text", "content": clean, "meal": meal})
    except gem.GeminiError as e:
        ss.messages.append({"role": "assistant", "kind": "text", "content": str(e)})
    st.rerun()


views.render_header(ss.name)
main, side = st.columns([2.2, 1], gap="large")

with main:
    if not ss.messages:
        views.render_empty_state(ss.name)
        a, b, c = st.columns(3)
        if a.button("Analyze a meal", use_container_width=True):
            ss.show_upload = True
        if b.button("Ask about nutrition", use_container_width=True):
            queue("Give me a quick tip for getting enough protein in a day.")
        if c.button("Log what you ate", use_container_width=True):
            queue("I want to log a meal. Ask me what I ate.")
    for m in ss.messages:
        views.render_message(m)

    with st.expander("Analyze a meal photo (JPG, JPEG, PNG)", expanded=ss.get("show_upload", False)):
        up = st.file_uploader("Upload photo", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        if up is not None:
            st.image(up, width=200, caption="Preview")
            if st.button("Analyze this photo", type="primary"):
                data = up.getvalue()
                if valid_image(data):
                    ss.show_upload = False
                    queue(None, data, up.type)
                else:
                    st.error("That doesn't look like a valid image under 8 MB. Try another photo.")

    if ss.pending:
        process_pending()

with side:
    views.render_snapshot(ss.messages)
    ready = any(m.get("meal") for m in ss.messages) or len(ss.messages) >= 2
    if views.render_whatsapp_card(ready):
        slot = st.empty()
        slot.markdown(views.thinking("Building your nutrition summary..."), unsafe_allow_html=True)
        try:
            summary, _ = gem.split_meal(gem.ask(ss.chat, [SUMMARY_REQUEST_PROMPT]))
            ok, msg = wa.send(secrets, ss.number, ss.name, summary)
        except gem.GeminiError as e:
            ok, msg = False, str(e)
        slot.empty()
        (st.success if ok else st.error)("Sent. Check your WhatsApp." if ok else msg)

chat_in = st.chat_input("Ask about a meal, or attach a photo", accept_file=True,
                        file_type=["jpg", "jpeg", "png"])
if chat_in and not ss.pending:
    photo = chat_in.files[0] if chat_in.files else None
    text = (chat_in.text or "").strip()
    if photo is not None:
        data = photo.getvalue()
        if not valid_image(data):
            st.error("That doesn't look like a valid image under 8 MB.")
        else:
            queue(text or None, data, photo.type)
    elif text:
        queue(text)
