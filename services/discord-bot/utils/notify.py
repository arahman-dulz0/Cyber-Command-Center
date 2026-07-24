"""
Optional email notifier (SMTP).

Disabled unless SMTP_HOST + SMTP_TO are configured. Sends off the event loop
(smtplib is blocking) via a thread executor. Never raises to the caller.
"""

from __future__ import annotations

import asyncio
import smtplib
from email.message import EmailMessage

from config import config
from utils.logger import get_logger

log = get_logger("notify")


def _send_blocking(subject: str, body: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = config.smtp_from or config.smtp_user or "cyber@localhost"
    msg["To"] = config.smtp_to
    msg.set_content(body)

    with smtplib.SMTP(config.smtp_host, config.smtp_port, timeout=20) as s:
        s.ehlo()
        try:
            s.starttls()
            s.ehlo()
        except smtplib.SMTPException:
            pass  # server without STARTTLS
        if config.smtp_user:
            s.login(config.smtp_user, config.smtp_password)
        s.send_message(msg)


async def send_email(subject: str, body: str) -> bool:
    """Send an email if the notifier is configured. Returns success (best-effort)."""
    if not config.email_enabled:
        return False
    try:
        await asyncio.get_running_loop().run_in_executor(None, _send_blocking, subject, body)
        log.info("Email notification sent: %s", subject)
        return True
    except Exception as exc:  # noqa: BLE001
        log.warning("Email notification failed: %s", exc)
        return False
