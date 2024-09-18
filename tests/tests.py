from datetime import datetime
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase, tag
from django.utils import timezone
from django.core import mail
from django.conf import settings

from django_user_activation.utils import TokenGenerator
from django_user_activation.activate import send_activation_email
from django_user_activation.views import activation_view


User = get_user_model()


class TestUserActivation(TestCase):
    def setUp(self):
        self.request = self.client.request().wsgi_request
        self.token_generator = TokenGenerator()

        self.user = User.objects.create_user(username='testuser', password='password', email='example@example.com', is_active=False)
        self.subject = getattr(settings, 'USER_ACTIVATION_EMAIL_SUBJECT', 'Email Verification')

    @tag('utils')
    def test_token_generator_create_token(self):
        token, expiry = self.token_generator.create_token(self.user.pk, timezone.now().timestamp() + 3600)
        self.assertIsInstance(token, str)
        self.assertIsInstance(expiry, datetime)

        with self.assertRaises(ValueError):
            self.token_generator.create_token('', timezone.now().timestamp() + 3600)

        with self.assertRaises(ValueError):
            self.token_generator.create_token(self.user.pk, 'invalid_expiry')

    @tag('utils')
    def test_token_generator_validate_token_invalid(self):
        message = self.token_generator.validate_token('invalid_token')
        self.assertEqual(message, 'Error, invalid token!')

    @tag('utils')
    def test_token_generator_validate_token_expired(self):
        token, _ = self.token_generator.create_token(self.user.pk, timezone.now().timestamp())
        message = self.token_generator.validate_token(token)
        self.assertEqual(message, 'Error, token has expired!')

    @tag('utils')
    def test_token_generator_validate_token_already_active(self):
        token, _ = self.token_generator.create_token(self.user.pk, timezone.now().timestamp() + 3600)
        self.user.is_active = True
        self.user.save()

        message = self.token_generator.validate_token(token)
        self.assertEqual(message, 'This account has already been activated!')

    @tag('utils')
    def test_token_generator_validate_token_valid(self):
        token, _ = self.token_generator.create_token(self.user.pk, timezone.now().timestamp() + 3600)
        message = self.token_generator.validate_token(token)
        self.assertEqual(message, 'Your account is now active!')
        self.assertTrue(User.objects.get(pk=self.user.pk).is_active)

    @tag('activate')
    def test_send_activation_email(self):
        send_activation_email(self.request, self.user)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, self.subject)

    @tag('activate')
    def test_send_activation_email_validators(self):
        with self.assertRaises(ValueError):
            send_activation_email(self.request, '')

    @tag('views')
    def test_valid_token_user_activated(self):
        success_message = 'This account has already been activated!'
        with mock.patch(
            'django_user_activation.activate.token_generator.validate_token',
            return_value=success_message
        ):
            response = activation_view(self.request, 'valid_token')

        assert response.status_code == 200
        assert response.content.decode() == success_message
