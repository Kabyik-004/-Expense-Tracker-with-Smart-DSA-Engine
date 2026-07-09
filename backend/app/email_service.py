"""
Email service — SMTP email sending with HTML templates.
Uses Python stdlib smtplib (no additional dependencies).
Configuration is read from Flask app.config (populated from .env).
"""

import logging
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import current_app, render_template

logger = logging.getLogger(__name__)


def send_otp_email(to_email, otp):
    """
    Render the OTP email template and send it via SMTP.
    Returns True if the email was sent successfully, False otherwise.
    """
    html = render_template("emails/otp_email.html", otp=otp)
    subject = "Your Password Reset OTP — Expense Tracker"
    return send_email(to_email=to_email, subject=subject, html_body=html)


def send_email(to_email, subject, html_body):
    """
    Low-level SMTP send with retry. Reads config from flask current_app.config.
    Returns True on success, False on failure (never raises — prevents enumeration).
    """
    config = current_app.config

    smtp_host = config.get("MAIL_SERVER", "smtp.gmail.com")
    smtp_port = config.get("MAIL_PORT", 587)
    smtp_user = config.get("MAIL_USERNAME", "")
    smtp_pass = config.get("MAIL_PASSWORD", "")
    use_tls = config.get("MAIL_USE_TLS", True)
    sender = config.get("MAIL_DEFAULT_SENDER") or smtp_user

    if not smtp_user or not smtp_pass:
        logger.warning(
            "MAIL_USERNAME/MAIL_PASSWORD not configured — skipping email to %s",
            to_email,
        )
        return False

    msg = MIMEMultipart("alternative")
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    attempts = [(smtp_host, smtp_port, smtp_user, smtp_pass, use_tls)]

    for attempt in range(2):
        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                if use_tls:
                    server.starttls()
                if smtp_user:
                    server.login(smtp_user, smtp_pass)
                server.sendmail(sender, to_email, msg.as_string())

            logger.info(
                "Email sent to %s (attempt %d/2)", to_email, attempt + 1
            )
            return True

        except Exception as exc:
            logger.warning(
                "SMTP attempt %d/2 failed for %s: %s",
                attempt + 1,
                to_email,
                exc,
            )
            if attempt == 0:
                time.sleep(1)

    logger.error("All SMTP attempts failed for %s", to_email)
    return False
