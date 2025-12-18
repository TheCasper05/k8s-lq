"""
Custom email backend using Resend API.

This backend bypasses SMTP and uses Resend's HTTP API directly,
which avoids connectivity issues with SMTP ports that may be
blocked by hosting providers like DigitalOcean.
"""

import logging
from typing import Any

import requests
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import EmailMessage, EmailMultiAlternatives

logger = logging.getLogger(__name__)


class ResendAPIBackend(BaseEmailBackend):
    """
    Email backend that sends emails via Resend's HTTP API.

    This avoids SMTP connectivity issues while maintaining
    compatibility with Django's email system.
    """

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = getattr(settings, "RESEND_API_KEY", None)
        if not self.api_key:
            raise ValueError("RESEND_API_KEY must be set in settings")

    def send_messages(self, email_messages: list[EmailMessage]) -> int:
        """
        Send one or more EmailMessage objects and return the number sent.
        """
        if not email_messages:
            return 0

        num_sent = 0
        for message in email_messages:
            try:
                sent = self._send(message)
                if sent:
                    num_sent += 1
            except Exception as e:
                logger.exception(f"Failed to send email via Resend API: {e}")
                if not self.fail_silently:
                    raise

        return num_sent

    def _send(self, message: EmailMessage) -> bool:
        """
        Send a single email message via Resend API.
        """
        payload: dict[str, Any] = {
            "from": message.from_email or settings.DEFAULT_FROM_EMAIL,
            "to": message.to,
            "subject": message.subject,
        }

        if message.cc:
            payload["cc"] = message.cc

        if message.bcc:
            payload["bcc"] = message.bcc

        if message.reply_to:
            payload["reply_to"] = message.reply_to

        # Handle HTML content
        has_html = False
        if isinstance(message, EmailMultiAlternatives):
            logger.info(
                f"EmailMultiAlternatives detected with {len(message.alternatives)} alternatives"
            )
            for content, mimetype in message.alternatives:
                logger.info(f"Alternative mimetype: {mimetype}")
                if mimetype == "text/html":
                    payload["html"] = content
                    has_html = True
                    logger.info(f"HTML content set (length: {len(content)} characters)")
                    break
            if message.body:
                payload["text"] = message.body
                logger.info(
                    f"Text content set (length: {len(message.body)} characters)"
                )
        else:
            logger.info("Regular EmailMessage detected (not EmailMultiAlternatives)")
            if message.body.strip().startswith("<"):
                payload["html"] = message.body
                has_html = True
                logger.info("Detected HTML in body, using as HTML")
            else:
                payload["text"] = message.body
                logger.info("Using body as plain text")

        # Log warning if no HTML was found
        if not has_html:
            logger.warning("No HTML content found in email, sending as plain text only")
        else:
            logger.info("Email will be sent with HTML content")

        tags = message.extra_headers.get("X-Tags")
        if tags:
            payload["tags"] = [{"name": "category", "value": tags}]

        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
        )

        if response.status_code == 200:
            logger.info(f"Email sent successfully via Resend API: {response.json()}")
            return True
        else:
            error_msg = f"Resend API error: {response.status_code} - {response.text}"
            logger.error(error_msg)
            if not self.fail_silently:
                raise Exception(error_msg)
            return False
