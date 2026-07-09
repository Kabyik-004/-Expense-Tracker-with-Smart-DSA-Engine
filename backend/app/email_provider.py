"""
Email provider abstraction — pluggable backends for transactional email delivery.
Add new providers by subclassing EmailProvider and registering in _PROVIDERS.
"""

import logging
import time
from abc import ABC, abstractmethod

import requests

logger = logging.getLogger(__name__)


class EmailProvider(ABC):
    """Base class for email delivery providers."""

    @abstractmethod
    def send(self, to_email, subject, html_body):
        """
        Deliver an HTML email.
        Returns True on success, False on failure (never raises).
        """
        ...


class BrevoProvider(EmailProvider):
    """Send emails via the Brevo (Sendinblue) Transactional Email API."""

    URL = "https://api.brevo.com/v3/smtp/email"

    def __init__(self, config):
        self.api_key = config.get("BREVO_API_KEY", "") or ""
        self.sender_email = config.get("MAIL_DEFAULT_SENDER", "") or ""

    def send(self, to_email, subject, html_body):
        if not self.api_key:
            logger.warning(
                "Brevo: BREVO_API_KEY not configured — skipping email to %s",
                to_email,
            )
            return False

        if not self.sender_email:
            logger.warning(
                "Brevo: MAIL_DEFAULT_SENDER not configured — skipping email to %s",
                to_email,
            )
            return False

        payload = {
            "sender": {"name": "Expense Tracker", "email": self.sender_email},
            "to": [{"email": to_email}],
            "subject": subject,
            "htmlContent": html_body,
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": self.api_key,
        }

        for attempt in range(2):
            try:
                resp = requests.post(
                    self.URL,
                    json=payload,
                    headers=headers,
                    timeout=(5, 10),
                )

                if resp.status_code in (200, 201):
                    logger.info(
                        "Brevo: email sent to %s (attempt %d/2)",
                        to_email,
                        attempt + 1,
                    )
                    return True

                category = self._classify(resp.status_code, resp.text)
                logger.warning(
                    "Brevo: attempt %d/2 failed for %s — "
                    "category=%s status=%d body=%s",
                    attempt + 1,
                    to_email,
                    category,
                    resp.status_code,
                    resp.text,
                )

            except requests.exceptions.ConnectionError:
                logger.warning(
                    "Brevo: attempt %d/2 connection refused for %s — "
                    "unreachable host or DNS resolution failed",
                    attempt + 1,
                    to_email,
                )

            except requests.exceptions.ReadTimeout:
                logger.warning(
                    "Brevo: attempt %d/2 HTTP read timed out for %s — "
                    "server took longer than 10s to respond",
                    attempt + 1,
                    to_email,
                )

            except requests.exceptions.ConnectTimeout:
                logger.warning(
                    "Brevo: attempt %d/2 connection timed out for %s — "
                    "network unreachable or firewall blocked",
                    attempt + 1,
                    to_email,
                )

            except requests.exceptions.Timeout:
                logger.warning(
                    "Brevo: attempt %d/2 timed out for %s — "
                    "request exceeded the total timeout window",
                    attempt + 1,
                    to_email,
                )

            except requests.exceptions.RequestException as exc:
                logger.warning(
                    "Brevo: attempt %d/2 failed for %s — exception=%s",
                    attempt + 1,
                    to_email,
                    exc,
                )

            if attempt == 0:
                time.sleep(1)

        logger.error(
            "Brevo: all attempts exhausted for %s — "
            "email was not sent after 2 retries",
            to_email,
        )
        return False

    @staticmethod
    def _classify(status_code, body):
        """Return a human-readable label for the HTTP status code."""
        if status_code == 401:
            return "invalid_api_key"
        if status_code == 400:
            if body and ("sender" in body.lower() or "from" in body.lower()):
                return "invalid_sender"
            return "bad_request"
        if status_code == 404:
            return "not_found"
        if status_code == 429:
            return "rate_limited"
        if 400 <= status_code < 500:
            return "client_error"
        if 500 <= status_code < 600:
            return "server_error"
        return "unexpected"


# ── Provider registry ────────────────────────────────────────────────────────

_PROVIDERS = {
    "brevo": BrevoProvider,
}

# Reserved for future providers:
# "resend": ResendProvider,
# "mailgun": MailgunProvider,
# "sendgrid": SendGridProvider,
# "ses": SesProvider,


def get_provider(config):
    """
    Factory: return the EmailProvider instance configured for this app.
    Select the provider via the ``EMAIL_PROVIDER`` config key (default: ``brevo``).
    """
    name = (config.get("EMAIL_PROVIDER") or "brevo").lower()
    cls = _PROVIDERS.get(name)
    if cls is None:
        logger.error("Unknown email provider '%s' — falling back to brevo", name)
        cls = BrevoProvider
    return cls(config)
