from typing import Any, Tuple, Union
from datetime import datetime
import logging

from django.contrib.auth import get_user_model
from django.conf import settings
import jwt


logger = logging.getLogger(__name__)


class TokenGenerator:
    _secret = settings.SECRET_KEY

    def create_token(self, user_pk: Any, expiry: Union[datetime, float, int]) -> Tuple[str, datetime]:
        """
        Create a token for the given user.

        :param Any user_pk: The primary key of the user.
        :param datetime or UTC Unix timestamp (int) expiry:
        The expiry time of the token.

        :returns str, datetime: the token and the expiry time.
        """
        if not user_pk:
            raise ValueError('User primary key must be provided')
        if not expiry or not isinstance(expiry, (datetime, float, int)):
            raise ValueError('Expiry must be a datetime or a UTC Unix timestamp')
        exp = expiry.timestamp() if isinstance(expiry, datetime) else expiry

        payload = {
            'pk': user_pk,
            'exp': exp
        }

        return jwt.encode(payload, self._secret, algorithm='HS256'), datetime.fromtimestamp(exp)

    def validate_token(self, token: str) -> str:
        """
        Return the user associated with the given token if the token is valid.

        :param token: The token to validate.
        :returns str: A message indicating the result of the validation.
        """
        try:
            payload = jwt.decode(token, self._secret, algorithms=['HS256'])

            User_model = get_user_model()
            user = User_model.objects.get(pk=payload['pk'])
        except jwt.ExpiredSignatureError:
            return 'Error, token has expired!'
        except Exception:
            logger.exception('Error validating token')
            return 'Error, invalid token!'

        if user.is_active:
            return 'This account has already been activated!'
        else:
            user.is_active = True
            user.save()

        if getattr(settings, 'USER_ACTIVATION_LOGGER', False):
            logger.info(f'User {user.username} has been activated')

        return 'Your account is now active!'


token_generator = TokenGenerator()
