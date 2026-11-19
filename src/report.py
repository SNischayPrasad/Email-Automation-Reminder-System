"""
report.py
---------
Saves the results of a run as a CSV report and prints a summary.
"""

from datetime import datetime

import pandas as pd

from src import config
from src.logger import get_logger

log = get_logger()

REPORT_COLUMNS = [
    "run_time", "mode", "reminder_id", "contact_id", "name", "email",
    "template", "subject", "scheduled_for", "status", "error",
]


def save_report(results: list) -> str:
    """Write results to outputs/report_<timestamp>.csv and append to report_history.csv."""
    if not results:
        log.info("No results to report.")
        return ""

    df = pd.DataFrame(results, columns=REPORT_COLUMNS)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = config.OUTPUTS_DIR / f"report_{stamp}.csv"
    df.to_csv(report_path, index=False)

    # Running history across all runs (header only written the first time)
    history = config.OUTPUTS_DIR / "report_history.csv"
    df.to_csv(history, mode="a", index=False, header=not history.exists())

    print_summary(df)
    log.info(f"Report saved: {report_path.relative_to(config.BASE_DIR)}")
    return str(report_path)


def print_summary(df: pd.DataFrame) -> None:
    counts = df["status"].value_counts()
    total = len(df)
    sent = counts.get("SENT", 0) + counts.get("DRY_RUN", 0)
    failed = counts.get("FAILED", 0)
    rate = (sent / total * 100) if total else 0

    print("\n" + "=" * 50)
    print("              RUN SUMMARY")
    print("=" * 50)
    print(f"  Total processed : {total}")
    print(f"  Sent / Dry-run  : {sent}")
    print(f"  Failed          : {failed}")
    print(f"  Success rate    : {rate:.1f}%")
    print("-" * 50)
    print("  By template:")
    for template, n in df["template"].value_counts().items():
        print(f"    {template:<22} {n}")
    print("=" * 50 + "\n")
