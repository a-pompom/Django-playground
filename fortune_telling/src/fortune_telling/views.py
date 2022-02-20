from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string

from . import fortune as fortune_module


def index(request: HttpRequest) -> HttpResponse:
    """
    トップ画面表示

    :param request: HTTPリクエスト
    :return: トップ画面をボディに持つHTTPレスポンス
    """
    return HttpResponse(render_to_string('index.html'))


def fortune_telling(request: HttpRequest) -> HttpResponse:
    """
    おみくじ結果画面表示

    :param request: HTTPリクエスト
    :return: おみくじ結果画面をボディに持つHTTPレスポンス
    """
    fortune = fortune_module.tell_fortune()
    context = {
        'fortune': fortune
    }

    return HttpResponse(render_to_string('fortune.html', context=context))
