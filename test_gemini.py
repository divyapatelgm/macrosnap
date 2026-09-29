import traceback
from google import genai
from google.genai import types

import os
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "your-api-key-here"))

print("--- 1. plain text, no chat ---")
try:
    r = client.models.generate_content(model="gemini-3.5-flash", contents="Say hi")
    print("OK:", r.text)
except Exception:
    traceback.print_exc()

print("--- 2. chat with system prompt (what the app does) ---")
try:
    chat = client.chats.create(
        model="gemini-3.5-flash",
        config=types.GenerateContentConfig(system_instruction="You are a nutrition buddy."),
    )
    print("OK:", chat.send_message(["How many calories in a banana?"]).text)
except Exception:
    traceback.print_exc()