"""File locations and the tiny settings file (remembered email)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
DATA = ROOT / "data"
CACHE = DATA / "cache"


def asset(name):
    """Path of assets/<name> if it exists, else None."""
    path = ASSETS / name
    return path if path.exists() else None


def load_settings():
    try:
        return json.loads((DATA / "settings.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_settings(**values):
    DATA.mkdir(exist_ok=True)
    data = load_settings()
    data.update(values)
    (DATA / "settings.json").write_text(json.dumps(data), encoding="utf-8")
