# MacroSnap

Smart nutrition without the spreadsheet. Chat or snap a meal photo; Gemini estimates calories and macros, keeps context for follow-ups, and Twilio texts your summary to WhatsApp.

## Features
Onboarding, nutrition workspace with live totals and meal list, structured meal result cards, photo analysis, empty-state quick actions, WhatsApp daily summary, WhatsApp weekly recap, daily login streaks, "what should I eat next" AI recommendations, friendly errors (details go to the server log).

## Tech stack
Python 3.9+, Streamlit, Google Gemini (`google-genai`), Twilio WhatsApp.

## Structure
`app.py` flow and state · `config.py` secrets · `prompts.py` AI behaviour · `services/` Gemini + Twilio · `ui/styles.py` CSS · `ui/views.py` HTML/Streamlit renderers.

## Setup
1. `python -m venv venv` then activate (`source venv/bin/activate` or `.\venv\Scripts\Activate.ps1`).
2. `pip install -r requirements.txt`
3. Gemini key: aistudio.google.com > Get API key.
4. Twilio: sign up, copy Account SID and Auth Token, open Messaging > Try it out > WhatsApp, send the join code from your phone to the sandbox number (repeat after ~72h idle). Create a Text template in Content Template Builder: `Hi {{1}}, here's your MacroSnap summary:\n\n{{2}}` and note its Content SID (HX...).
5. `cp .streamlit/secrets.toml.example .streamlit/secrets.toml` and fill in all five values.

## Run
`streamlit run app.py` (opens http://localhost:8501)

## Deploy
Push to GitHub (never `secrets.toml`), create the app on share.streamlit.io with `app.py`, paste your secrets into Settings > Secrets.

## Security
Never commit `secrets.toml`. Rotate keys if leaked. Keys are read only on the server.

## Known limitations
Estimates are approximate, not medical advice. Chat memory lives in the browser session and resets on refresh. The sandbox only messages numbers that joined it. Daily bars use fixed reference values (2000 kcal).
