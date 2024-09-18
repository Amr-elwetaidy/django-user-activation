from django.http import HttpResponse

from .utils import token_generator


def activation_view(request, token):
    """Validate the token and activate the user if the token is valid."""
    message = token_generator.validate_token(token)
    return HttpResponse(message)
