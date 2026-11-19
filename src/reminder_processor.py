"""
reminder_processor.py
---------------------
The core workflow:

  contacts + reminders  ->  find DUE reminders  ->  personalise template
        ->  send (or dry-run)  ->  record status  ->  report
"""

import time
from datetime import datetime

import pandas as pd

from src import config
from src.data_loader import (
    is_valid_email, load_contacts, load_reminders, merge_reminders_with_contacts,
)
from src.email_sender import EmailSender
from src.logger import get_logger, get_result_logger
from src.template_engine import render

log = get_logger()
sent_log = get_result_logger("sent")
failed_log = get_result_logger("failed")


def get_due_reminders(df: pd.DataFrame, now: datetime, already_done: set) -> pd.DataFrame:
    """Reminders whose send_at time has arrived and that weren't processed yet."""
    due = df[(df["send_at"].notna()) & (df["send_at"] <= now)]
    return due[~due["reminder_id"].isin(already_done)]


def _validate(row: dict) -> str:
    """Return an error message, or '' if the row is OK to send."""
    if not row["name"] and not row["email"]:
        return f"Unknown contact_id '{row['contact_id']}'"
    if not is_valid_email(row["email"]):
        return f"Invalid email address '{row['email']}'"
    if pd.isna(row["send_at"]):
        return "Invalid send_at date"
    return ""


def process_reminders(dry_run: bool = True, send_all: bool = False, already_done: set = None) -> list:
    """
    Process every due reminder once.

    dry_run      : True = don't actually send.
    send_all     : True = ignore send_at and process everything now (demo/testing).
    already_done : reminder_ids processed earlier (used by the scheduler loop).
    Returns a list of result dicts (one per reminder).
    """
    already_done = already_done if already_done is not None else set()
    contacts = load_contacts()
    reminders = load_reminders()
    data = merge_reminders_with_contacts(reminders, contacts)
    log.info(f"Loaded {len(contacts)} contacts and {len(reminders)} reminders.")

    now = datetime.now()
    if send_all:
        due = data[~data["reminder_id"].isin(already_done)]
    else:
        due = get_due_reminders(data, now, already_done)
    log.info(f"{len(due)} reminder(s) due at {now:%Y-%m-%d %H:%M}.")

    results = []
    if due.empty:
        return results

    mode = "DRY_RUN" if dry_run else "LIVE"
    with EmailSender(dry_run=dry_run) as sender:
        for row in due.to_dict("records"):
            result = {
                "run_time": now.strftime("%Y-%m-%d %H:%M:%S"),
                "mode": mode,
                "reminder_id": row["reminder_id"],
                "contact_id": row["contact_id"],
                "name": row["name"],
                "email": row["email"],
                "template": row["template"],
                "subject": "",
                "scheduled_for": row["send_at"].strftime(config.DATETIME_FORMAT) if pd.notna(row["send_at"]) else "",
                "status": "",
                "error": "",
            }
            try:
                error = _validate(row)
                if error:
                    raise ValueError(error)

                subject, body = render(row["template"], row)
                result["subject"] = subject
                sender.send(row["email"], subject, body, reminder_id=row["reminder_id"])

                result["status"] = "DRY_RUN" if dry_run else "SENT"
                log.info(f"[{result['status']}] {row['reminder_id']} -> {row['email']} | {subject}")
                sent_log.info(f"{row['reminder_id']} | {row['email']} | {subject} | {mode}")
                if not dry_run:
                    time.sleep(config.SEND_DELAY_SECONDS)  # be polite to the SMTP server

            except Exception as exc:  # one bad row must never stop the whole batch
                result["status"] = "FAILED"
                result["error"] = str(exc)
                log.error(f"[FAILED]  {row['reminder_id']} -> {row['email'] or '?'} | {exc}")
                failed_log.info(f"{row['reminder_id']} | {row['email'] or '?'} | {exc}")

            already_done.add(row["reminder_id"])
            results.append(result)

    return results
