from pytest import MonkeyPatch

from django.http.response import HttpResponse
from django.test.client import Client
from django.urls import reverse

from fortune_telling.urls import app_name
from fortune_telling import fortune


class TestIndex:
    """ トップ画面を表示できるか """

    # viewからレスポンスが得られるか
    def test_status_code(self):
        # GIVEN
        client = Client()
        request_name = f'{app_name}:index'
        # WHEN
        actual = client.get(reverse(request_name))
        # THEN
        assert actual.status_code == 200


class TestFortuneTelling:
    """ おみくじ結果が得られるか """

    # viewからレスポンスが得られるか
    def test_status_code(self):
        # GIVEN
        client = Client()
        request_name = f'{app_name}:fortune_telling'
        # WHEN
        actual: HttpResponse = client.get(reverse(request_name))
        # THEN
        assert actual.status_code == 200

    # HTMLを組み立てるコンテキストオブジェクトが存在するか
    def test_context(self):
        # GIVEN
        client = Client()
        request_name = f'{app_name}:fortune_telling'
        context_key_of_fortune = 'fortune'
        # WHEN
        actual: HttpResponse = client.get(reverse(request_name))
        context: dict = getattr(actual, 'context')
        # THEN
        assert context.get(context_key_of_fortune, None) is not None

    # コンテキストの運勢要素は関数から生成されたか
    def test_context_fortune(self, monkeypatch: MonkeyPatch):
        # GIVEN
        client = Client()
        request_name = f'{app_name}:fortune_telling'
        context_key_of_fortune = 'fortune'
        expected_fortune = '大吉'
        monkeypatch.setattr(fortune, 'tell_fortune', lambda: expected_fortune)

        # WHEN
        actual: HttpResponse = client.get(reverse(request_name))
        context: dict = getattr(actual, 'context')
        # THEN
        assert context.get(context_key_of_fortune, None) == expected_fortune
