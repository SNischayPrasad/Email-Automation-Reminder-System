"""
email_sender.py
---------------
Builds and sends emails.

Two modes:
  * DRY-RUN (default): nothing is sent. The email is printed/saved to
    outputs/dry_run_emails/ so you can inspect exactly what would go out.
  * LIVE: connects to an SMTP server (e.g. Gmail) with TLS and sends.
"""

import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr

from src import config
from src.logger import get_logger

log = get_logger()


class EmailSender:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.server = None
        self.preview_dir = config.OUTPUTS_DIR / "dry_run_emails"

    # ---- context manager: `with EmailSender() as s:` opens/closes SMTP once ----
    def __enter__(self):
        if self.dry_run:
            self.preview_dir.mkdir(parents=True, exist_ok=True)
            log.info("DRY-RUN mode: no real emails will be sent.")
        else:
            self._connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.server:
            try:
                self.server.quit()
            except smtplib.SMTPException:
                pass
            log.info("SMTP connection closed.")

    def _connect(self):
        if not config.smtp_is_configured():
            raise RuntimeError(
                "SMTP_USER / SMTP_PASSWORD are not set. Create a .env file "
                "(copy .env.example) or run in dry-run mode."
            )
        log.info(f"Connecting to {config.SMTP_HOST}:{config.SMTP_PORT} ...")
        self.server = smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=30)
        self.server.starttls(context=ssl.create_default_context())  # encrypt connection
        self.server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        log.info("SMTP login successful.")

    @staticmethod
    def build_message(to_email: str, subject: str, body: str) -> EmailMessage:
        msg = EmailMessage()
        msg["From"] = formataddr((config.SENDER_NAME, config.SMTP_USER or "noreply@example.com"))
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)
        return msg

    def send(self, to_email: str, subject: str, body: str, reminder_id: str = "") -> None:
        """Send one email. Raises an exception on failure (caller logs it)."""
        msg = self.build_message(to_email, subject, body)

        if self.dry_run:
            preview = self.preview_dir / f"{reminder_id or 'email'}.eml"
            preview.write_text(msg.as_string(), encoding="utf-8")
            return

        self.server.send_message(msg)
