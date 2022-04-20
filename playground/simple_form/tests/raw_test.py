from django.test.client import Client
from django.urls import reverse


class TestRawGet:
    """ formへのGETリクエストを検証 """

    # リクエストから期待通りのステータスコード・テンプレートが得られるか
    def test_success_request(self):
        # GIVEN
        client = Client()
        named_url = 'form:raw_get'
        expected_status_code = 200
        expected_template = 'raw_form.html'

        actual = client.get(reverse(named_url))
        # THEN
        assert actual.status_code == expected_status_code
        assert actual.templates[0].name == expected_template


class TestRawPost:
    """ formへのPOSTリクエストを検証 """

    # リクエストが成功するか
    def test_success_post(self):
        # GIVEN
        client = Client()
        named_url = 'form:raw_post'
        expected_status_code = 200
        # WHEN
        actual = client.post(reverse(named_url))
        # THEN
        assert actual.status_code == expected_status_code

    # リクエストから対応するコンテキストを組み立てられるか
    def test_context(self):
        # GIVEN
        client = Client()
        named_url = 'form:raw_post'
        form_data = {
            'text': 'hello world',
            'checkbox': ['dog', 'cat'],
            'radio': 'rice',
            'select': 'りんご',
        }
        expected = {
            'text': 'hello world',
            'checkbox': 'dog, cat',
            'radio': 'rice',
            'select': 'りんご',
        }

        # WHEN
        response = client.post(reverse(named_url), form_data)
        actual = {
            'text': response.context.get('text', None),
            'checkbox': response.context.get('checkbox', None),
            'radio': response.context.get('radio', None),
            'select': response.context.get('select', None),
        }

        # THEN
        assert actual == expected

    # POSTが成功した後、結果画面へのテンプレートが得られるか
    def test_success_post_template(self):
        # GIVEN
        client = Client()
        named_url = 'form:raw_post'
        expected = 'raw_form_result.html'

        # WHEN
        response = client.post(reverse(named_url))
        actual = response.context.template.name

        # THEN
        assert actual == expected

    # GETリクエストはform画面へリダイレクトされるか
    def test_redirect_get(self):
        # GIVEN
        client = Client()
        named_url = 'form:raw_post'
        expected = 'raw_form.html'

        # WHEN
        # キーワード引数followを設定しておくことで、redirect結果もレスポンスへ反映される
        response = client.get(reverse(named_url), follow=True)
        actual = response.context.template.name

        # THEN
        assert hasattr(response, 'redirect_chain')
        assert actual == expected
