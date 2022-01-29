from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .fortune import tell_fortune


def index(request: HttpRequest) -> HttpResponse:
    """
    トップ画面表示

    :param request: HTTPリクエスト
    :return: トップ画面をボディに持つHTTPレスポンス
    """
    return render(request, 'index.html')


def fortune_telling(request: HttpRequest) -> HttpResponse:
    """
    おみくじ結果画面表示

    :param request: HTTPリクエスト
    :return: おみくじ結果画面をボディに持つHTTPレスポンス
    """
    fortune = tell_fortune()
    context = {
        'fortune': fortune
    }

    return render(request, 'fortune.html', context)
