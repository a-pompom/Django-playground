from django.http import HttpRequest, HttpResponse


def hello_world(request: HttpRequest) -> HttpResponse:
    """
    Hello World文字列をレスポンスとして生成

    :param request: HTTPリクエスト
    :return: Hello World文字列をボディとするHTTPレスポンス
    """
    return HttpResponse('Hello World')
