"""
sample_data.py
--------------
Generates DUMMY contacts and reminders for safe simulation.

All emails use example.com / example.org - domains reserved for testing,
so even a mistaken live run cannot reach a real person.

Reminder send times are relative to *now*, so the demo always works:
some reminders are already due, some become due in 1-3 minutes
(to show the scheduler), and some are days away.
"""

from datetime import datetime, timedelta

import pandas as pd

from src import config

CONTACTS = [
    # contact_id, name, email, department, role
    ("C001", "Aarav Sharma",   "aarav.sharma@example.com",   "Sales",      "Sales Executive"),
    ("C002", "Priya Nair",     "priya.nair@example.com",     "HR",         "HR Manager"),
    ("C003", "Rohan Verma",    "rohan.verma@example.com",    "Finance",    "Accountant"),
    ("C004", "Sneha Iyer",     "sneha.iyer@example.org",     "Operations", "Ops Lead"),
    ("C005", "Karan Mehta",    "karan.mehta@example.com",    "Training",   "Trainee"),
    ("C006", "Ananya Reddy",   "ananya.reddy@example.org",   "Marketing",  "Webinar Host"),
    ("C007", "Vikram Singh",   "vikram.singh@example",       "Sales",      "Client"),        # invalid email on purpose
    ("C008", "Meera Joshi",    "meera.joshi@example.com",    "Admin",      "Office Admin"),
    ("C009", "Arjun Kapoor",   "arjun.kapoor@example.com",   "Engineering","Developer"),
    ("C010", "Divya Pillai",   "divya.pillai@example.org",   "Finance",    "Client"),
]


def build_reminders(now: datetime) -> list:
    fmt = config.DATETIME_FORMAT
    t = lambda **kw: (now + timedelta(**kw)).strftime(fmt)
    # reminder_id, contact_id, template, event_title, event_datetime, send_at, extra_info
    return [
        ("R001", "C001", "meeting_reminder", "Quarterly Sales Review",    t(hours=2),  t(minutes=-10), "Conference Room B / Google Meet"),
        ("R002", "C002", "task_notification","Submit appraisal forms",    t(days=1),   t(minutes=-5),  "Upload to HR portal"),
        ("R003", "C003", "payment_reminder", "Invoice #INV-2041",         t(days=3),   t(minutes=-1),  "Amount due: Rs. 18,500"),
        ("R004", "C004", "follow_up",        "Vendor onboarding call",    t(days=-1),  t(minutes=-2),  "Please share the signed NDA"),
        ("R005", "C005", "webinar_reminder", "Python Automation Webinar", t(hours=1),  t(minutes=-3),  "https://example.com/webinar/python"),
        ("R006", "C006", "meeting_reminder", "Campaign Planning",         t(hours=3),  t(minutes=1),   "Marketing Bay, 2nd floor"),
        ("R007", "C007", "payment_reminder", "Invoice #INV-2042",         t(days=2),   t(minutes=-4),  "Amount due: Rs. 7,200"),   # will FAIL (bad email)
        ("R008", "C008", "task_notification","Renew office insurance",    t(days=5),   t(minutes=2),   "Policy expires this month"),
        ("R009", "C099", "follow_up",        "Demo feedback",             t(days=-2),  t(minutes=-6),  "How was the product demo?"),  # will FAIL (unknown contact)
        ("R010", "C009", "webinar_reminder", "Git & GitHub Workshop",     t(days=1),   t(minutes=3),   "https://example.com/webinar/git"),
        ("R011", "C010", "payment_reminder", "Invoice #INV-2043",         t(days=7),   t(days=2),      "Amount due: Rs. 42,000"),  # future - stays WAITING
        ("R012", "C001", "follow_up",        "Proposal discussion",       t(days=-3),  t(days=1),      "Any questions on the proposal?"),
    ]


def generate(now: datetime = None) -> None:
    now = (now or datetime.now()).replace(second=0, microsecond=0)
    config.DATA_DIR.mkdir(exist_ok=True)
    pd.DataFrame(CONTACTS, columns=["contact_id", "name", "email", "department", "role"]) \
        .to_csv(config.CONTACTS_FILE, index=False)
    pd.DataFrame(build_reminders(now), columns=[
        "reminder_id", "contact_id", "template", "event_title",
        "event_datetime", "send_at", "extra_info",
    ]).to_csv(config.REMINDERS_FILE, index=False)
    print(f"Sample data written to data/ ({len(CONTACTS)} contacts, 12 reminders, base time {now:%Y-%m-%d %H:%M}).")


if __name__ == "__main__":
    generate()
