from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.shortcuts import render, redirect

from ..forms.validation_form import ValidationForm


def get(request: HttpRequest) -> HttpResponse:
    """
    入力画面を組み立てる
    
    :param request: HTTPリクエスト
    :return: 入力画面を表現するHTTPレスポンス
    """
    context = {
        'form': ValidationForm()
    }
    return render(request, 'validation_form.html', context=context)


def post(request: HttpRequest) -> HttpResponse:
    """
    入力画面からのPOSTリクエストを処理
    
    :param request: HTTPリクエスト
    :return: 結果画面を表現するHTTPレスポンス
    """

    if request.method == 'GET':
        return redirect(reverse('form:validation_get'))

    form = ValidationForm(request.POST)
    context = {
        'form': form
    }
    # バリデーション
    if not form.is_valid():
        return render(request, 'validation_form.html', context=context)

    return render(request, 'validation_form_result.html', context=context)
