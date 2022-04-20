from typing import cast
from django.http import HttpRequest, HttpResponse, QueryDict
from django.urls import reverse
from django.shortcuts import render, redirect


def get(request: HttpRequest) -> HttpResponse:
    """
    Formオブジェクトを利用しない生のフォームへのGETリクエストを処理

    :param request: HttpRequest
    :return: 生のフォームによる画面を表現するHTTPレスポンス
    """
    return render(request, 'raw_form.html')


def post(request: HttpRequest) -> HttpResponse:
    """
    Formオブジェクトを利用しない生のフォームへのPOSTリクエストを処理

    :param request: HttpRequest
    :return: 生のフォームによる画面を表現するHTTPレスポンス
    """
    if request.method != 'POST':
        return redirect(reverse('form:raw_get'))

    # request.POSTはQueryDictクラス型とみなされる
    # 実体はQueryDictインスタンスなので、キャストしておく
    body: QueryDict = cast(QueryDict, request.POST)

    # コンテキスト生成
    text = body.get('text', '')
    checkbox = ', '.join(body.getlist('checkbox', []))
    radio = body.get('radio', '')
    select = body.get('select', '')
    context = {
        'text': text,
        'checkbox': checkbox,
        'radio': radio,
        'select': select,
    }
    # 今回はセッションやDBを利用しないので、リダイレクトせずにそのまま結果画面へ
    return render(request, 'raw_form_result.html', context)
