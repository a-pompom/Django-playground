import logging
from django.http import HttpRequest, HttpResponse

from .models import Sample

logger = logging.getLogger(__name__)


def get(request: HttpRequest) -> HttpResponse:
    """
    ログへ記録するリクエスト・レスポンスを処理

    :param request: HTTPリクエスト
    :return: HTTPレスポンス
    """

    logger.info('%s %s REQUEST', request.method, request.path_info)

    # SQLがログへ出力されるか検証用
    sample = Sample.objects.get(text='hello')

    response = HttpResponse('Log')
    logger.info('%s %s %s RESPONSE', request.method, request.path_info, response.status_code)
    return HttpResponse(response)
