from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.urls import reverse

from .usecase.actions import SaveAction, ResultViewAction


def index(request: HttpRequest) -> HttpResponse:
    """
    トップ画面
    :param request: HTTPリクエスト
    :return: トップ画面のテンプレートから組み立てられたHTTPレスポンス
    """
    return render(request, 'index.html')


def save(request: HttpRequest) -> HttpResponse:
    """
    ユーザ登録処理
    :param request: HTTPリクエスト
    :return: ユーザ登録結果画面へのリダイレクトを表現するHTTPレスポンス
    """
    user = SaveAction()(request.POST['username'])

    return redirect(reverse('ユーザ登録:登録結果', args=[user.id]))


def result(request: HttpRequest, user_id: int) -> HttpResponse:
    """
    ユーザ登録結果画面
    :param request: HTTPリクエスト
    :param user_id: 表示対象ユーザの識別子
    :return: ユーザ登録結果画面を表現するHTTPレスポンス
    """
    return render(request, 'result.html', context=ResultViewAction()(user_id))
