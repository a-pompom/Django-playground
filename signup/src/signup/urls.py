from django.urls import path

from .views import index, save, result

app_name = 'ユーザ登録'

urlpatterns = [
    path('', index, name='トップ'),
    path('save', save, name='登録'),

    path('result/<int:user_id>', result, name='登録結果'),
]
