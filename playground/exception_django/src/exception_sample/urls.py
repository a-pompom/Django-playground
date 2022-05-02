from django.urls import path

from .views import get, raise_exception, handle_404, handle_500

handler404 = handle_404
handler500 = handle_500

urlpatterns = [
    path('', get),
    path('invalid', raise_exception)
]
