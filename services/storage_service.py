"""
Tiny local persistence layer, so goals, meal history and streaks survive a
browser refresh (session_state alone does not). Backed by one JSON file.

This is intentionally simple for a solo/portfolio project: a single file,
read-modify-write under a lock. It is NOT safe for many concurrent users
hammering it at once, and on Streamlit Community Cloud the file resets
whenever the app redeploys or sleeps, since the filesystem isn't persistent
there. For anything beyond a demo, swap this for a real database.
"""
import json
import logging
import os
from datetime import date, timedelta
from threading import Lock

log = logging.getLogger("macrosnap.storage")
_LOCK = Lock()
_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
_PATH = os.path.join(_DIR, "store.json")

_EMPTY_DAY = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "meals": []}
_EMPTY_USER = {"name": "", "goals": None, "streak": {"count": 0, "last_date": None}, "days": {}}


def _today():
    return date.today().isoformat()


def _load():
    try:
        with open(_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(db):
    os.makedirs(_DIR, exist_ok=True)
    tmp = _PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(db, f)
    os.replace(tmp, _PATH)


def get_user(number):
    with _LOCK:
        db = _load()
    return db.get(number, dict(_EMPTY_USER))


def save_goals(number, name, goals):
    with _LOCK:
        db = _load()
        u = db.setdefault(number, dict(_EMPTY_USER))
        u["name"], u["goals"] = name, goals
        _save(db)


def record_meal(number, meal):
    """Add a meal to today's totals and bump the logging streak. Returns streak count."""
    with _LOCK:
        db = _load()
        u = db.setdefault(number, dict(_EMPTY_USER))
        today = _today()
        day = u["days"].setdefault(today, dict(_EMPTY_DAY))
        day["meals"] = list(day["meals"])  # avoid aliasing the template list
        for k in ("calories", "protein", "carbs", "fat"):
            day[k] += int(meal.get(k, 0))
        day["meals"].append(str(meal.get("name", "Meal")))

        s = u.setdefault("streak", {"count": 0, "last_date": None})
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        if s.get("last_date") == today:
            pass  # already logged today, streak unchanged
        elif s.get("last_date") == yesterday:
            s["count"] = s.get("count", 0) + 1
            s["last_date"] = today
        else:
            s["count"], s["last_date"] = 1, today
        try:
            _save(db)
        except Exception:
            log.exception("Could not persist meal - continuing without it")
        return s["count"]


def get_today(number):
    return get_user(number)["days"].get(_today(), dict(_EMPTY_DAY))


def get_week(number):
    """Last 7 days, oldest first, zero-filled for days with nothing logged."""
    u = get_user(number)
    out = []
    for i in range(6, -1, -1):
        d = (date.today() - timedelta(days=i)).isoformat()
        out.append({"date": d, **u["days"].get(d, dict(_EMPTY_DAY))})
    return out


def get_streak(number):
    return get_user(number).get("streak", {}).get("count", 0)
