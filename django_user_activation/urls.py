from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import activation_view


urlpatterns = [
    path('activate/<str:token>', csrf_exempt(activation_view), name='user-activation'),
]
