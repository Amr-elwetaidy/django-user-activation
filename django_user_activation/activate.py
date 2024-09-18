import logging

from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.http import HttpRequest

from .utils import token_generator


logger = logging.getLogger(__name__)

EXPIRY = getattr(settings, f'USER_ACTIVATION_TOKEN_LIFE', 60*60)
SUBJECT = getattr(settings, 'USER_ACTIVATION_EMAIL_SUBJECT', 'Email Verification')
USE_CELERY = getattr(settings, f'USER_ACTIVATION_WITH_CELERY', False)
LOG = getattr(settings, f'USER_ACTIVATION_LOGGER', False)

try:
    EXPIRY = float(EXPIRY)
    assert EXPIRY > 0
    EXPIRY += timezone.now().timestamp()
except Exception:
    raise ValueError('`USER_ACTIVATION_TOKEN_LIFE` must be a number greater than 0')


def send_activation_email(request: HttpRequest, user):
    """
    Send an activation email to the user.

    :param HttpRequest request: The request object.
    :param User user: The user to send the activation email to.
    """
    from django.contrib.auth.models import User

    if not user or not isinstance(user, User):
        raise ValueError('A valid user object is required')

    email = user.email
    if not email:
        raise ValueError('Email is required')

    token, expiry = token_generator.create_token(user.pk, EXPIRY)

    activation_url = reverse('user-activation', args=[token])
    context = {
        'expiry': expiry,
        'link': request.build_absolute_uri(activation_url)
    }

    try:
        html = render_to_string('user_activation.html', context)
        text = render_to_string('user_activation.txt', context)
    except TemplateDoesNotExist:
        raise TemplateDoesNotExist(
            'Missing User Activation Templates. '
            'Please add user_activation.html and user_activation.txt to your templates directory'
        )

    if USE_CELERY:
        try:
            from .tasks import queue_email

            queue_email.delay(SUBJECT, text, html, [email])
            if LOG:
                logger.info(f'Activation email queued for {email}')

            return
        except ImportError:
            logger.error('Celery is not installed, sending email synchronously')

    try:
        send_mail(SUBJECT, text, None, [email], html_message=html)
        if LOG:
            logger.info(f'Activation email sent to {email}')
    except Exception as e:
        logger.error(f'Failed to send activation email to {email}: {e}')
