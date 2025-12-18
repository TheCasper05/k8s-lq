"""
Custom adapters for django-allauth.
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from allauth.account.adapter import DefaultAccountAdapter


class HTMLEmailAdapter(DefaultAccountAdapter):
    """
    Custom adapter that sends emails with both HTML and plain text versions.

    By default, allauth only sends plain text emails even if HTML templates exist.
    This adapter overrides the send_mail method to send EmailMultiAlternatives
    with both text and HTML versions.
    """

    def send_mail(self, template_prefix, email, context):
        """
        Send an email with both HTML and plain text versions.

        Args:
            template_prefix: The prefix for the email template files
            email: The recipient email address
            context: The context dictionary for rendering templates
        """
        # Add current_site to context if not present
        if "current_site" not in context:
            from django.contrib.sites.models import Site

            context["current_site"] = Site.objects.get_current()

        # Add user_display if not present
        if "user_display" not in context and "user" in context:
            user = context["user"]
            context["user_display"] = (
                user.get_full_name() or user.username or user.email.split("@")[0]
            )

        # Render subject (from .txt file)
        subject = render_to_string(f"{template_prefix}_subject.txt", context)
        subject = " ".join(subject.splitlines()).strip()
        subject = self.format_email_subject(subject)

        # Render plain text message (from .txt file)
        text_content = render_to_string(f"{template_prefix}_message.txt", context)

        # Try to render HTML message (from .html file)
        import logging

        logger = logging.getLogger(__name__)

        try:
            html_template_name = f"{template_prefix}_message.html"
            logger.info(f"Attempting to render HTML template: {html_template_name}")
            html_content = render_to_string(html_template_name, context)
            logger.info(
                f"HTML template rendered successfully, length: {len(html_content)}"
            )
        except Exception as e:
            # If HTML template doesn't exist, fall back to text only
            logger.warning(
                f"Failed to render HTML template {template_prefix}_message.html: {e}"
            )
            html_content = None

        from_email = self.get_from_email()

        if html_content:
            # Send email with both text and HTML versions
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=[email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        else:
            # Fall back to plain text only
            super().send_mail(template_prefix, email, context)
