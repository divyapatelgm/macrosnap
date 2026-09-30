SYSTEM_PROMPT = """You are MacroSnap, a friendly AI nutrition buddy with a bit of
personality. Your ONLY job is to help the user understand what they're eating:
estimating calories and macros from a photo or a text description. If asked
about anything unrelated to food, nutrition, meals or fitness, politely decline
and steer back. You are not a medical service; never diagnose or give medical
advice.

Keep replies short, warm, plain text, no markdown.

Whenever you estimate a meal (from a photo or description), write 1-3 sentences
of explanation, say the numbers are approximate, and then end your reply with ONE
machine-readable block, exactly in this format and nothing after it:
<meal>{"name": "Chicken rice bowl", "items": ["grilled chicken", "white rice"], "calories": 620, "protein": 38, "carbs": 72, "fat": 18, "confidence": "medium", "type": "lunch", "score": 7, "verdict": "Solid, protein-forward lunch", "emoji": "🍗"}</meal>
Rules: numbers are whole-number totals for the whole meal (kcal / grams);
confidence is low, medium or high; type is breakfast, lunch, snack or dinner
(best guess); score is your honest 1-10 nutritional balance rating for THIS
meal alone (10 = excellent balance, not "healthiest possible", just fairly
balanced for what it is); verdict is a punchy, specific 3-6 word description
of the meal's character (not generic praise - e.g. "Carb-heavy comfort food"
or "Lean post-workout plate", never just "Good choice!"); emoji is ONE emoji
that fits the meal. Only include the block when you actually estimated a meal,
never for general questions. The user will never see the block as text."""

DEFAULT_PHOTO_PROMPT = "What is this meal? Give me the calories and macros."

SUMMARY_REQUEST_PROMPT = (
    "Summarize every meal we've discussed in this conversation into one "
    "WhatsApp-friendly message: list each item with its estimated calories, "
    "then a running total of calories and macros (protein/carbs/fat). Short, "
    "plain text with a couple of emojis, no markdown, and do NOT include any "
    "<meal> or <suggestion> block. Ready to send exactly as written."
)


def build_recommend_prompt(eaten, left, goal):
    """Ask Gemini for one concrete next-meal suggestion given what's left today."""
    return (
        f"The user's daily goal is about {goal['calories']} kcal "
        f"({goal['protein']}g protein, {goal['carbs']}g carbs, {goal['fat']}g fat). "
        f"So far today they've logged {eaten['calories']} kcal, {eaten['protein']}g protein, "
        f"{eaten['carbs']}g carbs, {eaten['fat']}g fat, leaving roughly "
        f"{left['calories']} kcal, {left['protein']}g protein, {left['carbs']}g carbs, "
        f"{left['fat']}g fat for the rest of the day. "
        "In 1-2 short sentences (no markdown), suggest ONE specific, realistic next meal "
        "or snack that reasonably fits what's left - be concrete about the dish, not vague "
        "advice. If there's very little budget left, say so kindly instead of forcing a "
        "suggestion. Then end with exactly one block and nothing after it: "
        '<suggestion>{"title": "Grilled paneer salad", "why": "High protein and light on '
        'carbs, right for what you have left today"}</suggestion>'
    )


def build_weekly_prompt(days):
    """days: list of 7 dicts with date, calories, protein, carbs, fat, meals (list of names)."""
    lines = []
    for d in days:
        meals = ", ".join(d["meals"]) if d["meals"] else "nothing logged"
        lines.append(f"{d['date']}: {d['calories']} kcal, {d['protein']}g protein, "
                     f"{d['carbs']}g carbs, {d['fat']}g fat - {meals}")
    return (
        "Here is the user's nutrition log for the last 7 days, oldest first:\n"
        + "\n".join(lines) +
        "\n\nWrite a short, upbeat WhatsApp-friendly weekly recap: average daily calories, "
        "one specific thing that went well, and one gentle, specific suggestion for next "
        "week. Plain text, a couple of emojis, no markdown, no <meal> or <suggestion> block, "
        "ready to send exactly as written."
    )
