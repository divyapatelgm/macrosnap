import base64
import html
import streamlit as st

BRAND = '<div class="brand"><i></i>MacroSnap</div>'


def esc(t):
    return html.escape(t or "")


def render_onboarding(on_submit, presets):
    st.markdown(f'<div class="topbar">{BRAND}<span class="chip">Smart nutrition, no spreadsheet</span></div>',
                unsafe_allow_html=True)
    left, right = st.columns([1.3, 1], gap="large")
    with left:
        st.markdown("""<div class="hero"><h1>Know what <em>you're</em> eating.</h1>
<p>Snap a photo of your meal or just describe it. MacroSnap estimates calories and macros
in seconds, scores each meal, suggests what to eat next, and texts your summary to WhatsApp.</p>
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
            preset = st.selectbox("Daily goal", list(presets.keys()) + ["Custom"], index=1,
                                  help="A rough starting point you can change anytime. Not medical advice.")
            custom_kcal = None
            if preset == "Custom":
                custom_kcal = st.number_input("Daily calorie target", min_value=1000, max_value=5000,
                                              value=2000, step=50)
            go = st.form_submit_button("Start tracking", use_container_width=True)
        st.markdown('<p class="privacy">Used only to send summaries you request. '
                    'Estimates are approximate and not medical advice.</p>', unsafe_allow_html=True)
        if go:
            on_submit(name, number, preset, custom_kcal)


def render_header(name, streak):
    badge = f'<span class="streak">🔥 {streak}-day streak</span>' if streak >= 1 else ""
    st.markdown(f'<div class="topbar">{BRAND}<div style="display:flex;gap:.6rem;align-items:center">'
                f'{badge}<span class="chip">Today &middot; {esc(name)}</span></div></div>',
                unsafe_allow_html=True)


def _score_class(score):
    return "hi" if score >= 8 else ("mid" if score >= 5 else "lo")


def meal_card(m):
    items = ", ".join(esc(i) for i in m["items"])
    score = m.get("score", 7)
    badge = (f'<span class="score-badge {_score_class(score)}" '
             f'aria-label="Nutrition balance score: {score} out of 10">{score}/10</span>')
    return f"""<div class="result"><div class="tag">{esc(m.get('emoji','🍽️'))} MEAL DETECTED{badge}</div>
<h3>{esc(m['name'])}</h3><div class="verdict">{esc(m.get('verdict','Logged'))}</div>
<div class="items">{items}</div><div class="grid">
<div><b>{m['calories']}</b><span>kcal</span></div><div><b>{m['protein']} g</b><span>Protein</span></div>
<div><b>{m['carbs']} g</b><span>Carbs</span></div><div><b>{m['fat']} g</b><span>Fat</span></div></div>
<div class="note">Estimate &middot; {esc(m['confidence'])} confidence. Photo-based numbers are approximate.</div></div>"""


def suggestion_card(s):
    why = f'<p>{esc(s["why"])}</p>' if s.get("why") else ""
    return f"""<div class="suggestion"><div class="tag">SUGGESTION</div>
<h4>{esc(s['title'])}</h4>{why}</div>"""


def render_message(m):
    if m["kind"] == "image":
        b64 = base64.b64encode(m["content"]).decode()
        body = f'<img src="data:image/jpeg;base64,{b64}" alt="Meal photo you uploaded">'
    else:
        body = f'<div class="body">{esc(m["content"])}</div>' if m["content"] else ""
        if m.get("meal"):
            body += meal_card(m["meal"])
        if m.get("suggestion"):
            body += suggestion_card(m["suggestion"])
    cls, who = ("user", "You") if m["role"] == "user" else ("ai", "MacroSnap")
    st.markdown(f'<div class="msg {cls}"><div class="who">{who}</div>{body}</div>', unsafe_allow_html=True)


def thinking(text):
    return f'<div class="think" role="status"><i></i><i></i><i></i><span>{esc(text)}</span></div>'


def render_empty_state(name):
    st.markdown(f"""<div class="empty"><div class="msg ai"><div class="who">MacroSnap</div><div class="body">Hi {esc(name)}, I'm your nutrition buddy. Describe a meal or drop in a photo and I'll break it down - or ask me what to eat next.</div></div>
<h2>Your nutrition story starts here.</h2><p>Pick a place to begin.</p></div>""", unsafe_allow_html=True)


def render_snapshot(today, goals, streak):
    pct = min(100, round(today["calories"] / max(goals["calories"], 1) * 100))
    out = f"""<div class="snap"><h4>Nutrition snapshot</h4>
<div class="ring-wrap"><div class="ring" style="--pct:{pct}"><div class="hole">
<b>{today['calories']}</b><span>of {goals['calories']} kcal</span></div></div></div>"""
    for k, label in (("protein", "Protein"), ("carbs", "Carbs"), ("fat", "Fat")):
        w = min(100, round(today[k] / max(goals[k], 1) * 100))
        out += (f'<div class="macro"><div class="row"><span>{label}</span>'
               f'<b>{today[k]} / {goals[k]} g</b></div><div class="bar"><span style="width:{w}%"></span></div></div>')
    out += '<h4 style="margin-top:1.4rem">Meals today</h4>'
    out += "".join(f'<div class="meal"><div>{esc(name)}</div></div>' for name in today["meals"]) \
        or '<p class="chip">No meals logged yet.</p>'
    st.markdown(out + "</div>", unsafe_allow_html=True)


def render_whatsapp_card(daily_enabled, week_enabled):
    st.markdown('<div class="wa"><b>Send a nutrition summary</b>'
                '<p>Get your meals and totals delivered to WhatsApp.</p></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    daily = c1.button("Today", disabled=not daily_enabled, use_container_width=True, type="primary",
                      help=None if daily_enabled else "Log a meal or ask a question first.")
    weekly = c2.button("This week", disabled=not week_enabled, use_container_width=True,
                       help=None if week_enabled else "No meals logged this week yet.")
    return daily, weekly
