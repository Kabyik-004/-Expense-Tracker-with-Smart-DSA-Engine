"""
Email service — application-level interface for sending transactional emails.
Delegates delivery to the configured provider via a background thread pool
so API responses never wait for email transmission.
"""

import logging
from concurrent.futures import ThreadPoolExecutor

from flask import current_app, render_template

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=4)


def send_otp_email(to_email, otp):
    """
    Render the OTP email template and dispatch it via the configured provider.
    Returns True if the email was submitted for delivery, False otherwise.
    """
    html = render_template("emails/otp_email.html", otp=otp)
    subject = "Your Password Reset OTP — Expense Tracker"
    return send_email(to_email=to_email, subject=subject, html_body=html)


def send_email(to_email, subject, html_body):
    """
    Queue an HTML email for background delivery via the configured provider.
    Returns True immediately (submission accepted), never raises.
    """
    app = current_app._get_current_object()
    _executor.submit(_deliver, app, to_email, subject, html_body)
    return True


def _deliver(app, to_email, subject, html_body):
    """Background task: send one email with retry, then log the outcome."""
    with app.app_context():
        from app.email_provider import get_provider

        provider = get_provider(current_app.config)
        ok = provider.send(to_email, subject, html_body)

    if ok:
        logger.info("Background email sent to %s", to_email)
    else:
        logger.error(
            "Background email delivery failed for %s after all retries",
            to_email,
        )
