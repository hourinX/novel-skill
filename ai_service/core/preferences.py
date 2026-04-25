import json
from pathlib import Path
from datetime import date


PREFERENCES_PATH = Path("data/preferences.json")

DEFAULT_PREFERENCES = {
    "preferred_genre": "玄幻",
    "writing_style": "紧张大气",
    "chapter_length": 8000,
    "narrative_perspective": "第三人称有限视角",
    "hook_preference": "悬念型",
    "last_updated": str(date.today()),
}


def read_preferences() -> dict:
    if not PREFERENCES_PATH.exists():
        return DEFAULT_PREFERENCES.copy()
    with open(PREFERENCES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def write_preferences(prefs: dict) -> None:
    PREFERENCES_PATH.parent.mkdir(parents=True, exist_ok=True)
    prefs["last_updated"] = str(date.today())
    with open(PREFERENCES_PATH, "w", encoding="utf-8") as f:
        json.dump(prefs, f, ensure_ascii=False, indent=2)


def update_preference(key: str, value) -> None:
    prefs = read_preferences()
    prefs[key] = value
    write_preferences(prefs)