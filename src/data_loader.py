"""
data_loader.py
--------------
Reads contacts.csv and reminders.csv with pandas and validates them.
"""

import re
from pathlib import Path

import pandas as pd

from src import config

CONTACT_COLUMNS = ["contact_id", "name", "email", "department", "role"]
REMINDER_COLUMNS = [
    "reminder_id", "contact_id", "template", "event_title",
    "event_datetime", "send_at", "extra_info",
]

# Simple email pattern - good enough to catch typos like "abc@" or "abc.com"
EMAIL_PATTERN = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.match(str(email).strip()))


def _check_columns(df: pd.DataFrame, required: list, file: Path) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{file.name} is missing columns: {missing}")


def load_contacts(path: Path = config.CONTACTS_FILE) -> pd.DataFrame:
    """Load contacts. Each row = one person who can receive reminders."""
    if not path.exists():
        raise FileNotFoundError(f"Contacts file not found: {path}")
    df = pd.read_csv(path, dtype=str).fillna("")
    _check_columns(df, CONTACT_COLUMNS, path)
    df["email"] = df["email"].str.strip()
    return df


def load_reminders(path: Path = config.REMINDERS_FILE) -> pd.DataFrame:
    """Load reminders and convert date columns to real datetime objects."""
    if not path.exists():
        raise FileNotFoundError(f"Reminders file not found: {path}")
    df = pd.read_csv(path, dtype=str).fillna("")
    _check_columns(df, REMINDER_COLUMNS, path)
    # errors="coerce" turns bad dates into NaT instead of crashing
    df["event_datetime"] = pd.to_datetime(df["event_datetime"], format=config.DATETIME_FORMAT, errors="coerce")
    df["send_at"] = pd.to_datetime(df["send_at"], format=config.DATETIME_FORMAT, errors="coerce")
    return df


def merge_reminders_with_contacts(reminders: pd.DataFrame, contacts: pd.DataFrame) -> pd.DataFrame:
    """
    Join reminders to contacts on contact_id (like a SQL LEFT JOIN).
    Reminders pointing to an unknown contact keep empty name/email,
    so they are reported as FAILED instead of silently disappearing.
    """
    merged = reminders.merge(contacts, on="contact_id", how="left")
    return merged.fillna({"name": "", "email": "", "department": "", "role": ""})
