from django.test import Client
from django.urls import reverse

from src.simple_form.forms.validation_form import ValidationForm


class TestViewGet:
    """ Formオブジェクトから入力要素を組み立てる画面へのGETリクエストを検証 """

    named_url = 'form:validation_get'

    # GETリクエストからValidationFormを含むコンテキストによって描画された
    # form画面を表現するHTTPレスポンスが得られるか
    def test_success(self):
        # GIVEN
        expected_template_name = 'validation_form.html'
        expected_context_form_type = ValidationForm
        client = Client()

        # WHEN
        response = client.get(reverse(self.named_url))
        actual_template_name = response.context.template.name
        actual_context = response.context
        actual_context_form = actual_context.get('form', None)
        assert actual_context_form is not None
        actual_context_form_classname = actual_context_form.__class__.__name__

        # THEN
        assert actual_template_name == expected_template_name
        assert actual_context_form_classname == expected_context_form_type.__name__


class TestPost:
    """ Formオブジェクトから入力要素を組み立てる画面へのPOSTリクエストを検証 """
    
    def test_success(self):
        pass
    
    def test_validation_error(self):
        pass
    
    def test_get_request(self):
        pass
