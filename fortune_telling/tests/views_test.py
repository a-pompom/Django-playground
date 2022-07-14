from pytest import MonkeyPatch

from django.http.response import HttpResponse
from django.test.client import Client
from django.urls import reverse

from fortune_telling import fortune


class TestIndex:
    """ トップ画面を表示できるか """

    # viewからレスポンスが得られるか
    def test_status_code(self):
        # GIVEN
        client = Client()
        named_url = 'おみくじ:トップ'
        # WHEN
        actual = client.get(reverse(named_url))
        # THEN
        assert actual.status_code == 200

    # トップ画面のテンプレートを参照しているか
    def test_use_index_template(self, assertion_helper):
        # GIVEN
        client = Client()
        named_url = 'おみくじ:トップ'
        expected = 'index.html'
        # WHEN
        response = client.get(reverse(named_url))
        # THEN
        assertion_helper.assert_template_used(response, expected)


class TestFortuneTelling:
    """ おみくじ結果が得られるか """

    # viewからレスポンスが得られるか
    def test_status_code(self):
        # GIVEN
        client = Client()
        named_url = 'おみくじ:結果'
        # WHEN
        actual: HttpResponse = client.get(reverse(named_url))
        # THEN
        assert actual.status_code == 200

    # 結果画面のテンプレートを参照しているか
    def test_use_result_template(self, assertion_helper):
        # GIVEN
        client = Client()
        named_url = 'おみくじ:結果'
        expected = 'fortune.html'
        # WHEN
        response = client.get(reverse(named_url))
        # THEN
        assertion_helper.assert_template_used(response, expected)

    # コンテキストの運勢要素は関数から生成されたか
    def test_context_fortune(self, monkeypatch: MonkeyPatch, assertion_helper):
        # GIVEN
        client = Client()
        named_url = 'おみくじ:結果'
        context_key_of_fortune = 'fortune'
        expected = '大吉'
        # GIVEN-MOCK
        monkeypatch.setattr(fortune, 'tell_fortune', lambda: expected)

        # WHEN
        response = client.get(reverse(named_url))
        # THEN
        assertion_helper.assert_context_get(response, context_key_of_fortune, expected)
