from django.urls import path

from .views import index, fortune_telling

app_name = 'おみくじ'
urlpatterns = [
    path('', index, name='トップ'),
    path('fortune_telling/', fortune_telling, name='結果')
]
