from django.urls import path

from .views import index, fortune_telling

app_name = 'fortune_telling'
urlpatterns = [
    path('', index, name='index'),
    path('fortune_telling/', fortune_telling, name='fortune_telling')
]
