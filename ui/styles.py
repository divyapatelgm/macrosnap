import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap');
:root{--ink:#16161a;--paper:#f6f2e9;--card:#fffdf8;--lime:#c8f169;--lime-d:#5f7d12;--mute:#6b6a64;--line:#e2dccd;
--serif:'Fraunces',Georgia,serif;--sans:'Inter',system-ui,sans-serif}
#MainMenu,footer,header[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important}
.stApp{background:var(--paper);font-family:var(--sans);color:var(--ink)}
.block-container{max-width:1120px;padding:1.2rem 1.5rem 7rem}
h1,h2,h3{font-family:var(--serif)!important;letter-spacing:-.02em;color:var(--ink)}
.brand{display:flex;align-items:center;gap:.5rem;font-family:var(--serif);font-weight:600;font-size:1.3rem}
.brand i{width:.85rem;height:.85rem;border-radius:50%;background:var(--lime);border:2px solid var(--ink);display:inline-block}
.topbar{display:flex;justify-content:space-between;align-items:center;padding:.4rem 0 1.2rem;border-bottom:1px solid var(--line);margin-bottom:1.4rem}
.chip{font-size:.8rem;color:var(--mute)}
.hero h1{font-size:clamp(2.4rem,6vw,4.2rem);line-height:1.02;margin:.3rem 0 1rem;font-weight:500}
.hero h1 em{background:linear-gradient(transparent 62%,var(--lime) 62%);font-style:italic}
.hero p{color:var(--mute);font-size:1.05rem;max-width:34rem;line-height:1.55}
.plate{background:var(--ink);color:var(--paper);border-radius:14px;padding:1.3rem 1.4rem;margin-top:1.4rem;max-width:26rem}
.plate small{color:#a9a89f;letter-spacing:.12em;font-size:.68rem}
.plate b{font-family:var(--serif);font-size:1.5rem;display:block;margin:.2rem 0 .7rem;font-weight:500}
.bar{height:6px;border-radius:3px;background:#34343a;margin:.35rem 0 .7rem;overflow:hidden}.bar span{display:block;height:100%;background:var(--lime)}
.row{display:flex;justify-content:space-between;font-size:.85rem}
.privacy{font-size:.78rem;color:var(--mute);margin-top:.6rem}
/* inputs & buttons */
.stTextInput input{background:var(--card)!important;border:1px solid var(--line)!important;border-radius:8px!important;padding:.75rem!important;color:var(--ink)!important}
.stTextInput label p,.stFileUploader label p{font-size:.8rem;font-weight:600;color:var(--ink)}
.stButton>button,.stFormSubmitButton>button{border-radius:8px;border:1px solid var(--ink);background:var(--card);color:var(--ink);font-weight:600;min-height:2.6rem;transition:transform .12s,background .12s}
.stButton>button:hover,.stFormSubmitButton>button:hover{background:var(--lime);border-color:var(--ink);color:var(--ink);transform:translateY(-1px)}
.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"],.stFormSubmitButton>button{background:var(--ink);color:var(--paper)}
.stButton>button[kind="primary"]:hover,.stFormSubmitButton>button:hover{background:var(--lime);color:var(--ink)}
button:focus-visible,input:focus-visible,[data-testid="stChatInput"] textarea:focus-visible{outline:3px solid var(--lime-d)!important;outline-offset:2px}
[data-testid="stFileUploaderDropzone"]{background:var(--card);border:1.5px dashed var(--ink);border-radius:10px}
[data-testid="stChatInput"]{background:var(--card);border:1px solid var(--ink);border-radius:12px}
[data-testid="stBottom"]>div{background:var(--paper)}
.snap .bar{background:var(--line)}
.snap .bar span{background:var(--ink)}
/* conversation */
.msg{margin:0 0 1.15rem;max-width:42rem}
.msg .who{font-size:.68rem;letter-spacing:.12em;text-transform:uppercase;color:var(--mute);margin-bottom:.25rem}
.msg .body{line-height:1.55;white-space:pre-wrap}
.msg.user{margin-left:auto;text-align:right}
.msg.user .body{display:inline-block;text-align:left;background:var(--ink);color:var(--paper);padding:.65rem .95rem;border-radius:14px 14px 3px 14px}
.msg.ai .body{border-left:3px solid var(--lime);padding-left:.9rem}
.msg img{max-width:min(260px,100%);border-radius:10px;border:1px solid var(--line)}
.result{background:var(--card);border:1px solid var(--ink);border-radius:12px;padding:1rem 1.1rem;margin:.6rem 0 .2rem;box-shadow:4px 4px 0 var(--lime)}
.result .tag{font-size:.68rem;letter-spacing:.14em;color:var(--lime-d);font-weight:600}
.result h3{margin:.15rem 0 .1rem;font-size:1.45rem}
.result .items{color:var(--mute);font-size:.85rem;margin-bottom:.7rem}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:.5rem;border-top:1px solid var(--line);padding-top:.7rem}
.grid div b{display:block;font-family:var(--serif);font-size:1.35rem;font-weight:600}.grid div span{font-size:.72rem;color:var(--mute)}
.note{font-size:.74rem;color:var(--mute);margin-top:.6rem}
.think{display:flex;gap:.4rem;align-items:center;color:var(--mute);font-size:.9rem;margin:.4rem 0}
.think i{width:.45rem;height:.45rem;border-radius:50%;background:var(--ink);animation:b 1s infinite ease-in-out}
.think i:nth-child(2){animation-delay:.15s}.think i:nth-child(3){animation-delay:.3s}
@keyframes b{0%,80%,100%{opacity:.2}40%{opacity:1}}
.empty h2{font-size:2rem;margin:.2rem 0}.empty p{color:var(--mute);max-width:30rem}
/* snapshot */
.snap{border-left:1px solid var(--line);padding-left:1.3rem}
.snap h4{font-size:.68rem;letter-spacing:.14em;text-transform:uppercase;color:var(--mute);margin:0 0 .6rem;font-family:var(--sans)}
.big{font-family:var(--serif);font-size:3rem;line-height:1;font-weight:500}.big small{font-size:1rem;color:var(--mute);font-family:var(--sans)}
.macro{margin:.9rem 0 0}.macro .row b{font-weight:600}
.meal{display:flex;justify-content:space-between;padding:.5rem 0;border-bottom:1px solid var(--line);font-size:.88rem}
.meal span{color:var(--mute);font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;display:block}
.wa{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:.9rem 1rem;margin-top:1.3rem}
.wa b{font-family:var(--serif);font-size:1.1rem}.wa p{font-size:.8rem;color:var(--mute);margin:.2rem 0 .6rem}
@media(max-width:760px){.snap{border-left:0;padding-left:0;border-top:1px solid var(--line);padding-top:1rem}.grid{grid-template-columns:repeat(2,1fr)}.block-container{padding:.8rem .9rem 7rem}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}

/* --- new: goal ring, streak, score badge, suggestion card --- */
@property --pct{syntax:'<number>';inherits:true;initial-value:0}
.ring-wrap{display:flex;justify-content:center;margin:.2rem 0 1rem}
.ring{--pct:0;width:132px;height:132px;border-radius:50%;
  background:conic-gradient(var(--ink) calc(var(--pct)*1%), var(--line) 0);
  display:flex;align-items:center;justify-content:center;transition:--pct 1.1s ease-out}
.ring .hole{width:100px;height:100px;border-radius:50%;background:var(--paper);
  display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.ring .hole b{font-family:var(--serif);font-size:1.7rem;line-height:1;font-weight:500}
.ring .hole span{font-size:.68rem;color:var(--mute);margin-top:.15rem}
.streak{display:inline-flex;align-items:center;gap:.35rem;font-size:.8rem;color:var(--ink);
  background:var(--card);border:1px solid var(--line);border-radius:999px;padding:.25rem .7rem}
.score-badge{display:inline-flex;align-items:center;gap:.3rem;font-size:.78rem;font-weight:600;
  border:1px solid var(--ink);border-radius:999px;padding:.1rem .55rem;margin-left:.4rem}
.score-badge.hi{background:var(--lime)}
.score-badge.mid{background:var(--card)}
.score-badge.lo{background:var(--paper);color:var(--mute)}
.result .verdict{font-style:italic;color:var(--mute);font-size:.85rem;margin:.15rem 0 .6rem}
.suggestion{background:var(--card);border:1px solid var(--ink);border-radius:12px;
  padding:1rem 1.1rem;margin:.6rem 0;border-left:5px solid var(--lime)}
.suggestion .tag{font-size:.68rem;letter-spacing:.14em;color:var(--lime-d);font-weight:600}
.suggestion h4{font-family:var(--serif);font-size:1.2rem;margin:.2rem 0 .3rem;font-weight:600}
.suggestion p{font-size:.88rem;color:var(--mute);margin:0}
</style>
"""


def inject():
    st.markdown(CSS, unsafe_allow_html=True)
