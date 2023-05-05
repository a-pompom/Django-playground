from django.urls import path

from .views import get

urlpatterns = [
    path('', get, name='get'),
]
