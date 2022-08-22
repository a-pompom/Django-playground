import pytest
from django.urls import reverse
from django.test.client import Client

from signup.models import User
from .data.user import user_creation, user_exists


class TestIndex:
    """ ユーザ登録画面を表示できるか検証 """

    named_url = 'ユーザ登録:トップ'

    # 名前付きURLからviewを参照できるか
    def test_status_code(self):
        # GIVEN
        client = Client()
        expected = 200
        # WHEN
        response = client.get(reverse(self.named_url))
        actual = response.status_code
        # THEN
        assert actual == expected

    # テンプレートindex.htmlをもとにレスポンスを組み立てているか
    def test_template_used(self, assertion_helper):
        # GIVEN
        client = Client()
        # WHEN
        response = client.get(reverse(self.named_url))
        # THEN
        assertion_helper.assert_template_used(response, 'index.html')


@pytest.mark.django_db
class TestSave:
    """ ユーザ情報を登録し、結果画面へリダイレクトできるか検証 """

    named_url = 'ユーザ登録:登録'

    # ユーザ情報をデータベースに登録できるか
    def test_save(self):
        # GIVEN
        client = Client()
        username = 'Python'
        with user_creation():
            # WHEN
            client.post(reverse(self.named_url), {'username': username})
            actual = User.objects.get(username=username)
            # THEN
            assert actual.username == username

    # 登録後、結果画面へリダイレクトするか
    def test_redirect(self, assertion_helper):
        # GIVEN
        client = Client()
        username = 'Python'
        expected_user_id = 1
        expected = [reverse('ユーザ登録:登録結果', args=[expected_user_id])]
        with user_creation():
            # WHEN
            response = client.post(reverse(self.named_url), {'username': username}, follow=True)
            # THEN
            assertion_helper.assert_redirect_routes(response, expected)


@pytest.mark.django_db
class TestResult:
    """ ユーザ識別子からユーザ登録画面を組み立てられるか検証 """

    named_url = 'ユーザ登録:登録結果'

    # 結果画面のテンプレートを参照しているか
    def test_template(self, assertion_helper):
        # GIVEN
        client = Client()
        expected = 'result.html'

        with user_exists() as user:
            # WHEN
            response = client.post(reverse(self.named_url, args=[user.id]))
            # THEN
            assertion_helper.assert_template_used(response, expected)

    # コンテキストにユーザ情報を含むか
    def test_context(self, assertion_helper):
        # GIVEN
        client = Client()
        expected = User(username='Django')

        with user_exists() as user:
            # WHEN
            response = client.post(reverse(self.named_url, args=[user.id]))
            # THEN
            assertion_helper.assert_context_get(response, 'user', expected)
