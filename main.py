"""
Email Automation & Reminder System
==================================
Entry point. Examples:

    python main.py --generate-sample          # create fresh dummy data
    python main.py                            # dry-run: process due reminders once
    python main.py --all                      # dry-run: process ALL reminders now
    python main.py --schedule                 # dry-run: keep checking for due reminders
    python main.py --schedule --minutes 4     # same, auto-stop after 4 minutes
    python main.py --show                     # print the reminder schedule
    python main.py --live                     # REALLY send emails (needs .env)

Dry-run is the default. Real emails are only sent with --live.
"""

import argparse
import sys

from src import config
from src.logger import get_logger


def parse_args():
    p = argparse.ArgumentParser(description="Email Automation & Reminder System")
    p.add_argument("--live", action="store_true", help="send real emails via SMTP (default is dry-run)")
    p.add_argument("--all", action="store_true", help="process all reminders now, ignoring send_at")
    p.add_argument("--schedule", action="store_true", help="run continuously and send reminders when due")
    p.add_argument("--minutes", type=float, default=None, help="auto-stop the scheduler after N minutes")
    p.add_argument("--show", action="store_true", help="show the reminder schedule and exit")
    p.add_argument("--generate-sample", action="store_true", help="(re)create dummy data in data/")
    return p.parse_args()


def main():
    args = parse_args()
    config.ensure_folders()

    if args.generate_sample:
        from src.sample_data import generate
        generate()
        return

    log = get_logger()
    dry_run = not args.live

    from src.scheduler import run_scheduler, show_upcoming
    from src.reminder_processor import process_reminders
    from src.report import save_report

    if args.show:
        show_upcoming()
        return

    if args.live:
        if not config.smtp_is_configured():
            log.error("LIVE mode needs SMTP_USER and SMTP_PASSWORD in .env (see .env.example).")
            sys.exit(1)
        confirm = input("LIVE mode will send real emails. Type 'yes' to continue: ")
        if confirm.strip().lower() != "yes":
            print("Cancelled.")
            return

    print("\n=== Email Automation & Reminder System ===")
    print(f"Mode: {'LIVE (real emails)' if args.live else 'DRY-RUN (safe simulation)'}\n")

    try:
        if args.schedule:
            run_scheduler(dry_run=dry_run, max_minutes=args.minutes)
        else:
            results = process_reminders(dry_run=dry_run, send_all=args.all)
            save_report(results)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        log.error(exc)
        print("Tip: run  python main.py --generate-sample  to create sample data.")
        sys.exit(1)


if __name__ == "__main__":
    main()
