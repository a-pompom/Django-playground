from django.test import Client
from django.urls import reverse

from src.simple_form.forms.view_form import ViewForm


class TestViewGet:
    """ Formオブジェクトから入力要素を組み立てる画面へのGETリクエストを検証 """
    named_url = 'form:view_get'

    # ViewFormクラスのインスタンスがコンテキストのFormオブジェクトへ設定されているか
    def test_success_get(self):
        # GIVEN
        expected_template_name = 'view_form.html'
        expected_context_form_type = ViewForm
        client = Client()
        # WHEN
        response = client.get(reverse(self.named_url))
        actual_template_name = response.context.template.name
        actual_context_form = response.context.get('form', None)
        assert actual_context_form is not None
        actual_context_form_class_name = actual_context_form.__class__.__name__

        # THEN
        assert actual_template_name == expected_template_name
        assert actual_context_form_class_name == expected_context_form_type.__name__


class TestViewPost:
    """ Formオブジェクトから入力要素を組み立てる画面へのPOSTリクエストを検証 """

    named_url = 'form:view_post'

    # contextのFormのBoundFieldへ値が設定されているか
    def test_success_post(self):
        # GIVEN
        expected_template_name = 'view_form_result.html'
        form_data = {
            'text': 'hello world',
            'checkbox': ['dog', 'cat'],
            'radio': 'rice',
            'select': 'りんご',
        }
        expected_context = {
            'text': 'hello world',
            'checkbox': ['dog', 'cat'],
            'radio': 'rice',
            'select': 'りんご',
        }

        client = Client()

        # WHEN
        response = client.post(reverse(self.named_url), form_data)
        form = response.context.get('form', None)
        assert form is not None

        actual_context = {
            'text': form['text'].value(),
            'checkbox': form['checkbox'].value(),
            'radio': form['radio'].value(),
            'select': form['select'].value(),

        }
        # THEN
        assert actual_context == expected_context

        actual_template_name = response.context.template.name
        assert actual_template_name == expected_template_name
