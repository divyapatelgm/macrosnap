import base64
import html
import streamlit as st

TARGET_KCAL = 2000  # reference bar only, not medical advice
MAXES = {"protein": 150, "carbs": 250, "fat": 70}
BRAND = '<div class="brand"><i></i>MacroSnap</div>'


def esc(t):
    return html.escape(t or "")


def render_onboarding(on_submit):
    st.markdown(f'<div class="topbar">{BRAND}<span class="chip">Smart nutrition, no spreadsheet</span></div>',
                unsafe_allow_html=True)
    left, right = st.columns([1.3, 1], gap="large")
    with left:
        st.markdown("""<div class="hero"><h1>Know what <em>you're</em> eating.</h1>
<p>Snap a photo of your meal or just describe it. MacroSnap estimates calories and macros
in seconds, then texts your day's summary to WhatsApp.</p>
<div class="plate"><small>MEAL DETECTED</small><b>Chicken rice bowl</b>
<div class="row"><span>Protein</span><span>38 g</span></div><div class="bar"><span style="width:72%"></span></div>
<div class="row"><span>Carbs</span><span>72 g</span></div><div class="bar"><span style="width:85%"></span></div>
<div class="row"><span>Calories</span><span>~620 kcal</span></div></div>
<p class="privacy">Example only. Your real results come from your own meals.</p></div>""",
                    unsafe_allow_html=True)
    with right:
        st.markdown("<h3 style='margin-top:1rem'>Start tracking</h3>", unsafe_allow_html=True)
        with st.form("onboarding"):
            name = st.text_input("Your name", placeholder="Asha")
            number = st.text_input("WhatsApp number (with country code)", placeholder="+91XXXXXXXXXX")
            go = st.form_submit_button("Start tracking", use_container_width=True)
        st.markdown('<p class="privacy">Used only to send summaries you request. '
                    'Estimates are approximate and not medical advice.</p>', unsafe_allow_html=True)
        if go:
            on_submit(name, number)


def render_header(name):
    st.markdown(f'<div class="topbar">{BRAND}<span class="chip">Today &middot; {esc(name)}</span></div>',
                unsafe_allow_html=True)


def meal_card(m):
    items = ", ".join(esc(i) for i in m["items"])
    return f"""<div class="result"><div class="tag">MEAL DETECTED</div><h3>{esc(m['name'])}</h3>
<div class="items">{items}</div><div class="grid">
<div><b>{m['calories']}</b><span>kcal</span></div><div><b>{m['protein']} g</b><span>Protein</span></div>
<div><b>{m['carbs']} g</b><span>Carbs</span></div><div><b>{m['fat']} g</b><span>Fat</span></div></div>
<div class="note">Estimate &middot; {esc(m['confidence'])} confidence. Photo-based numbers are approximate.</div></div>"""


def render_message(m):
    if m["kind"] == "image":
        b64 = base64.b64encode(m["content"]).decode()
        body = f'<img src="data:image/jpeg;base64,{b64}" alt="Meal photo you uploaded">'
    else:
        body = f'<div class="body">{esc(m["content"])}</div>'
        if m.get("meal"):
            body += meal_card(m["meal"])
    cls, who = ("user", "You") if m["role"] == "user" else ("ai", "MacroSnap")
    st.markdown(f'<div class="msg {cls}"><div class="who">{who}</div>{body}</div>', unsafe_allow_html=True)


def thinking(text):
    return f'<div class="think" role="status"><i></i><i></i><i></i><span>{esc(text)}</span></div>'


def render_empty_state(name):
    st.markdown(f"""<div class="empty"><div class="msg ai"><div class="who">MacroSnap</div><div class="body">Hi {esc(name)}, I'm your nutrition buddy. Describe a meal or drop in a photo and I'll break it down.</div></div>
<h2>Your nutrition story starts here.</h2><p>Pick a place to begin.</p></div>""", unsafe_allow_html=True)


def totals(messages):
    meals = [m["meal"] for m in messages if m.get("meal")]
    t = {k: sum(x[k] for x in meals) for k in ("calories", "protein", "carbs", "fat")}
    return meals, t


def render_snapshot(messages):
    meals, t = totals(messages)
    pct = min(100, round(t["calories"] / TARGET_KCAL * 100))
    out = f'<div class="snap"><h4>Nutrition snapshot</h4><div class="big">{t["calories"]} <small>kcal</small></div>'
    out += f'<div class="bar"><span style="width:{pct}%"></span></div>'
    for k, label in (("protein", "Protein"), ("carbs", "Carbs"), ("fat", "Fat")):
        w = min(100, round(t[k] / MAXES[k] * 100))
        out += f'<div class="macro"><div class="row"><span>{label}</span><b>{t[k]} g</b></div><div class="bar"><span style="width:{w}%"></span></div></div>'
    out += '<h4 style="margin-top:1.4rem">Meals</h4>'
    out += "".join(f'<div class="meal"><div><span>{esc(x["type"])}</span>{esc(x["name"])}</div><b>{x["calories"]}</b></div>' for x in meals) \
        or '<p class="chip">No meals logged yet.</p>'
    st.markdown(out + "</div>", unsafe_allow_html=True)


def render_whatsapp_card(enabled):
    st.markdown('<div class="wa"><b>Send today\'s nutrition summary</b>'
                '<p>Get your meals and nutrition totals delivered to WhatsApp.</p></div>', unsafe_allow_html=True)
    return st.button("Send to WhatsApp", disabled=not enabled, use_container_width=True, type="primary",
                     help=None if enabled else "Log a meal or ask a question first.")
