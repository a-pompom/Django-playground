import logging

from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import render

from .exceptions import SampleException

logger = logging.getLogger(__name__)


def get(request: HttpRequest) -> HttpResponse:
    """
    通常の画面描画
    
    :param request: HTTPリクエスト
    :return: テスト用の画面を表現するHTTPレスポンス
    """
    return render(request, 'hello.html')


def raise_exception(request: HttpRequest) -> HttpResponse:
    """
    サーバエラーを擬似的に再現

    :param request: HTTPリクエスト
    :return: テスト用の画面を表現するHTTPレスポンス
    """
    logger.info('raise exception')
    try:
        # なにかの処理
        raise SampleException()
    except SampleException as e:
        logger.exception('SampleException %s %s %s', request.method, request.path_info, request.headers)
        raise
    return render(request, 'hello.html')


def handle_404(request: HttpRequest, e: Http404) -> HttpResponse:
    """
    404エラー画面描画

    :param request: HTTPリクエスト
    :param e: 404エラー
    :return: 404エラー用の画面を表現するHTTPレスポンス
    """
    return render(request, 'errors/404.html')


def handle_500(request: HttpRequest) -> HttpResponse:
    """
    500エラー画面描画

    :param request: HTTPリクエスト
    :return: 500エラー用の画面を表現するHTTPレスポンス
    """
    return render(request, 'errors/500.html')
