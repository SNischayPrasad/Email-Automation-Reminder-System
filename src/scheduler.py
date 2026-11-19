"""
scheduler.py
------------
Keeps the program running and checks for due reminders every N seconds
using the `schedule` library. Stop it with Ctrl + C.

In a real company this loop would be replaced by cron (Linux),
Windows Task Scheduler, or a cloud scheduler - but the logic is the same.
"""

import time
from datetime import datetime

import schedule

from src import config
from src.data_loader import load_reminders
from src.logger import get_logger
from src.reminder_processor import process_reminders
from src.report import save_report

log = get_logger()


def show_upcoming() -> None:
    """Print the reminder queue so you can see what is scheduled."""
    df = load_reminders().sort_values("send_at")
    now = datetime.now()
    print("\nREMINDER SCHEDULE")
    print("-" * 78)
    print(f"{'ID':<7}{'Template':<22}{'Send at':<18}{'Status':<10}Event")
    print("-" * 78)
    for _, r in df.iterrows():
        when = r["send_at"].strftime(config.DATETIME_FORMAT) if not r.isna()["send_at"] else "INVALID"
        state = "DUE" if (not r.isna()["send_at"] and r["send_at"] <= now) else "WAITING"
        print(f"{r['reminder_id']:<7}{r['template']:<22}{when:<18}{state:<10}{r['event_title']}")
    print("-" * 78 + "\n")


def run_scheduler(dry_run: bool = True, max_minutes: float = None) -> None:
    """
    Check every SCHEDULER_INTERVAL_SECONDS. `max_minutes` lets you auto-stop
    (handy for demos/tests); None = run until Ctrl + C.
    """
    done = set()        # remembers which reminders were already handled
    all_results = []

    def job():
        results = process_reminders(dry_run=dry_run, already_done=done)
        if results:
            save_report(results)
            all_results.extend(results)

    log.info(f"Scheduler started - checking every {config.SCHEDULER_INTERVAL_SECONDS}s. Press Ctrl+C to stop.")
    show_upcoming()
    job()  # run once immediately
    schedule.every(config.SCHEDULER_INTERVAL_SECONDS).seconds.do(job)

    start = time.time()
    try:
        while True:
            schedule.run_pending()
            if max_minutes and (time.time() - start) > max_minutes * 60:
                log.info("Reached max run time - stopping scheduler.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("Scheduler stopped by user.")
    finally:
        schedule.clear()
        log.info(f"Scheduler processed {len(all_results)} reminder(s) in total.")
