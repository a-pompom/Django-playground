from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.shortcuts import render, redirect

from ..forms.only_mapping_form import OnlyMappingForm


def get(request: HttpRequest) -> HttpResponse:
    """
    form画面描画

    :param request: HTTPリクエスト
    :return: form画面を表現するHTTPレスポンス
    """
    return render(request, 'only_mapping_form.html')


def post(request: HttpRequest) -> HttpResponse:
    """
    formから受け取ったPOSTリクエストを処理

    :param request: HTTPリクエスト
    :return: formの値を受け取った結果画面を表現するHTTPレスポンス
    """
    
    if request.method == 'GET':
        return redirect(reverse('form:only_mapping_get'))

    form = OnlyMappingForm(request.POST)
    form.is_valid()

    text = form.cleaned_data.get('text', '')
    checkbox = ', '.join(form.cleaned_data.get('checkbox', []))
    radio = form.cleaned_data.get('radio', '')
    select = form.cleaned_data.get('select', '')

    context = {
        'text': text,
        'checkbox': checkbox,
        'radio': radio,
        'select': select,
    }

    return render(request, 'only_mapping_form_result.html', context=context)
