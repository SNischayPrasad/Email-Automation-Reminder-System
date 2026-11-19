"""
config.py
---------
Central place for all settings.

Secrets (SMTP password etc.) are NEVER written in code. They are read from
environment variables, which can be stored locally in a `.env` file.
The `.env` file is listed in .gitignore so it never reaches GitHub.
"""

import os
from pathlib import Path

# python-dotenv is optional: if installed, it loads variables from .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ---------- Folder paths ----------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUTS_DIR = BASE_DIR / "outputs"
LOGS_DIR = BASE_DIR / "logs"

CONTACTS_FILE = DATA_DIR / "contacts.csv"
REMINDERS_FILE = DATA_DIR / "reminders.csv"

# ---------- SMTP settings (from environment) ----------
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")          # your Gmail address
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")  # Gmail App Password (NOT normal password)
SENDER_NAME = os.getenv("SENDER_NAME", "Reminder Bot")

# ---------- Behaviour ----------
# Pause between emails (seconds) so we don't get flagged as spam
SEND_DELAY_SECONDS = float(os.getenv("SEND_DELAY_SECONDS", "1"))
# How often the scheduler checks for due reminders (seconds)
SCHEDULER_INTERVAL_SECONDS = int(os.getenv("SCHEDULER_INTERVAL_SECONDS", "30"))
# Date-time format used in reminders.csv
DATETIME_FORMAT = "%Y-%m-%d %H:%M"


def smtp_is_configured() -> bool:
    """True only when both SMTP user and password are present."""
    return bool(SMTP_USER and SMTP_PASSWORD)


def ensure_folders() -> None:
    """Create output/log folders if they don't exist yet."""
    for folder in (OUTPUTS_DIR, LOGS_DIR):
        folder.mkdir(parents=True, exist_ok=True)
