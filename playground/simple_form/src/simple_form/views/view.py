from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.shortcuts import render, redirect

from ..forms.view_form import ViewForm


def get(request: HttpRequest) -> HttpResponse:
    """
    入力画面を組み立てることを責務に持つ

    :param request: HTTPリクエスト
    :return: 入力画面を表現するHTTPレスポンス
    """
    form = ViewForm()
    context = {
        'form': form
    }

    return render(request, 'view_form.html', context=context)


def post(request: HttpRequest) -> HttpResponse:
    """
    入力画面から受け取った入力要素をもとに結果画面を組み立てることを責務に持つ

    :param request: HTTPリクエスト
    :return: 結果画面を表現するHTTPレスポンス
    """

    if request.method == 'GET':
        return redirect(reverse('form:view_get'))

    form = ViewForm(request.POST)
    form.is_valid()

    context = {
        'form': form,
    }

    return render(request, 'view_form_result.html', context=context)
