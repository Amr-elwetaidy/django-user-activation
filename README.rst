======================
django-user-activation
======================

About
-----
django-user-activation is a Django app to manage user activation on registration.

Requirements
------------
- Python >= 3.10
- Django >= 5.0

Setup
-----
Install from **pip**:

.. code-block:: sh

    python -m pip install django-user-activation

and then add it to your installed apps:

.. code-block:: python

    INSTALLED_APPS = [
        ...,
        "django_user_activation",
        ...,
    ]

Configuration
-------------
- Ensure that django_user_activation's URLs are included in your project's `urls.py`:

    .. code-block:: python

        from django.urls import path, include

        urlpatterns = [
            ...,
            path('user/', include('django_user_activation.urls')),
            ...,
        ]

- Configure the behaviour in your Django settings:

    - ``USER_ACTIVATION_TOKEN_LIFE: int | float``

        The number of seconds that the activation token is valid for. Default is 3600 (1 hour).

    - ``USER_ACTIVATION_EMAIL_SUBJECT: str``

        The subject of the activation email. Default is "Email Verification".

    - ``USER_ACTIVATION_WITH_CELERY: bool``

        Whether to use Celery to send the activation email. Default is False.
        If set to True, you must have Celery set up and configured in your project.

    - ``USER_ACTIVATION_LOGGER: bool``

        Whether to log activation events. Default is False.

- Configure the email backend in your Django settings:

    .. code-block:: python

        EMAIL_HOST = 'smtp.example.com'
        EMAIL_PORT = 587
        EMAIL_USE_TLS = True
        EMAIL_HOST_USER = ''
        EMAIL_HOST_PASSWORD = ''

- Templates
    - You can override the templates used by django-user-activation by creating your own templates in your project under the ``templates/user_activation`` directory.
    - The templates that can be overridden are:
        - ``django_user_activation/user_activation.html``
        - ``django_user_activation/user_activation.txt``


Example Usage
-------------
.. code-block:: python

    ...
    from django_user_activation import send_activation_email
    ...


    def register(request):
        if request.method == "POST":
            form = UserRegistrationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                send_activation_email(request, user)
                ...

Testing
-------
To run the tests, clone the repository and install the requirements:

.. code-block:: sh

    python -m pip install -r requirements.txt

and then run:

.. code-block:: sh

    python manage.py test