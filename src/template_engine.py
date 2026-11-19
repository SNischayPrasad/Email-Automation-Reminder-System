"""
template_engine.py
------------------
Loads email templates from the templates/ folder and fills in placeholders.

Template file format (plain text):
    Subject: Reminder: {event_title} on {event_date}
    <blank line>
    Hi {first_name},
    ...body...

Placeholders use {curly_braces}. Any placeholder that has no value is left
visible (e.g. "{amount}") instead of crashing - easy to spot in dry-run.
"""

from functools import lru_cache
from pathlib import Path

from src import config


class SafeDict(dict):
    """dict that returns '{key}' for missing keys instead of raising KeyError."""
    def __missing__(self, key):
        return "{" + key + "}"


@lru_cache(maxsize=None)
def load_template(name: str) -> tuple:
    """
    Read templates/<name>.txt and split it into (subject, body).
    lru_cache means each file is read from disk only once.
    """
    path: Path = config.TEMPLATES_DIR / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path.name}")

    text = path.read_text(encoding="utf-8")
    first_line, _, body = text.partition("\n")
    if not first_line.lower().startswith("subject:"):
        raise ValueError(f"{path.name}: first line must start with 'Subject:'")
    subject = first_line.split(":", 1)[1].strip()
    return subject, body.strip()


def build_context(row: dict) -> dict:
    """Turn one merged reminder/contact row into template variables."""
    event_dt = row.get("event_datetime")
    name = str(row.get("name", "")).strip()
    return {
        "name": name,
        "first_name": name.split()[0] if name else "there",
        "email": row.get("email", ""),
        "department": row.get("department", ""),
        "role": row.get("role", ""),
        "event_title": row.get("event_title", ""),
        "event_date": event_dt.strftime("%d %b %Y") if hasattr(event_dt, "strftime") else "",
        "event_time": event_dt.strftime("%I:%M %p") if hasattr(event_dt, "strftime") else "",
        "extra_info": row.get("extra_info", ""),
        "sender_name": config.SENDER_NAME,
    }


def render(template_name: str, row: dict) -> tuple:
    """Return personalised (subject, body) for one recipient."""
    subject, body = load_template(template_name)
    ctx = SafeDict(build_context(row))
    return subject.format_map(ctx), body.format_map(ctx)
