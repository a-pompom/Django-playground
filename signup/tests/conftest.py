import os
from pathlib import Path
import pytest
import sys
from typing import Union, Optional

import django
from django.http import HttpResponse
from django.template.base import Template
from django.test.utils import ContextList
from django.template.context import Context


def pytest_sessionstart(session):
    """ Djangoテストの前処理 """

    # 各種モジュールをimportできるようsrcディレクトリをimportパスへ追加
    src_directory = Path(__file__).resolve().parent.parent / 'src'
    sys.path.append(str(src_directory))

    # 利用する設定ファイル
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    # Djangoの各種モジュールを参照するための準備を整える
    django.setup()


TypeRedirectChain = list[tuple[str, int]]


class ClientResponseAttribute(HttpResponse):
    """ TestClientがresponseオブジェクトへ注入する追加の属性を表現することを責務に持つ """
    templates: list[Template]
    context: Union[Context, ContextList]
    redirect_chain: Optional[TypeRedirectChain]


TypeClientResponse = ClientResponseAttribute


class AssertionHelper:
    """ django.test.TestCaseが担っていたassertionを表現することを責務に持つ """

    def assert_template_used(self, response: ClientResponseAttribute, template_name: str):
        """
        TestClientがレスポンスを生成したとき、指定のテンプレートファイルが利用されたことを表明

        :param response: TestClientが返却するレスポンスオブジェクト
        :param template_name: テンプレートファイル名
        """

        template_names = [template.name for template in response.templates if template.name is not None]
        assert template_name in template_names

    def assert_context_get(self, response: ClientResponseAttribute, key: str, value):
        """
        コンテキストオブジェクトのキーで対応する要素が期待通りであることを表明

        :param response: TestClientが返却するレスポンスオブジェクト
        :param key: コンテキストの対象キー
        :param value: 期待値
        """
        context = response.context
        assert context.get(key) == value

    def assert_redirect_routes(self, response: ClientResponseAttribute, routes: list[str]):
        """
        リダイレクト先が期待通りであることを表明

        :param response: TestClientが返却するレスポンスオブジェクト
        :param routes: リダイレクト先の期待値 複数リダイレクトすることもあるのでリスト形式とする
        """
        if not hasattr(response, 'redirect_chain'):
            print('Response does not have redirect_chain attribute.')
            assert False

        for redirect, route in zip(response.redirect_chain, routes):
            url, status_code = redirect
            assert route == url


# djangoのTestCaseで実装されているassertionをpytestでも実行するためのヘルパー
@pytest.fixture
def assertion_helper():
    return AssertionHelper()
