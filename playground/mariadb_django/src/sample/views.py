from django.http import HttpRequest, HttpResponse

from .models import Task


def get(request: HttpRequest) -> HttpResponse:
    """
    データベースへレコードを登録
    
    :param request: HTTP リクエスト
    :return: HTTP レスポンス
    """
    task = Task(text='Sample')
    task.save()

    return HttpResponse('Query OK')
