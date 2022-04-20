from django.test.client import Client
from django.urls import reverse


class TestOnlyMappingGet:
    """ form画面へのGETリクエストを検証 """

    # ステータスコードは200で、form画面を表現するテンプレートが得られるか
    def test_success_request(self):
        # GIVEN
        client = Client()
        named_url = 'form:only_mapping_get'
        expected_status_code = 200
        expected_template_name = 'only_mapping_form.html'

        # WHEN
        response = client.get(reverse(named_url))
        actual_status_code = response.status_code
        actual_template_name = response.context.template.name

        # THEN
        assert actual_status_code == expected_status_code
        assert actual_template_name == expected_template_name


class TestOnlyMappingPost:
    """ form画面へのPOSTリクエストを検証 """

    named_url = 'form:only_mapping_post'

    # 結果画面を表現するテンプレートが得られるか
    def test_template_name(self):
        # GIVEN
        client = Client()
        expected_status_code = 200
        expected_template_name = 'only_mapping_form_result.html'

        # WHEN
        response = client.get(reverse(self.named_url))
        actual_status_code = response.status_code
        actual_template_name = response.context.template.name

        # THEN
        assert actual_status_code == expected_status_code
        assert actual_template_name == expected_template_name

    # POSTリクエストをFormオブジェクトで処理することで、想定通りのコンテキストが得られるか
    def test_context(self):
        # GIVEN
        client = Client()
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
        response = client.post(reverse(self.named_url), data=form_data)
        actual = {
            'text': response.context.get('text', None),
            'checkbox': response.context.get('checkbox', None),
            'radio': response.context.get('radio', None),
            'select': response.context.get('select', None),
        }

        # THEN
        assert actual == expected

    # GETリクエストはform画面へリダイレクトされるか
    def test_get_request_redirect(self):
        # GIVEN
        client = Client()
        expected = 'only_mapping_form.html'
        # WHEN
        response = client.get(reverse(self.named_url), follow=True)
        actual = response.context.template.name

        # THEN
        assert hasattr(response, 'redirect_chain')
        assert actual == expected
