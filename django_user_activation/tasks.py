from django.core.mail import send_mail
from celery import shared_task


@shared_task(name='queue_email', bind=True, max_retries=3, default_retry_delay=60)
def queue_email(self, subject, text, html, emails):
    """Queue an email to be sent."""
    try:
        send_mail(subject, text, None, emails, html_message=html)
    except Exception:
        raise self.retry()
