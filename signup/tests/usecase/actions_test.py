import pytest

from signup.usecase.actions import SaveAction, ResultViewAction
from signup.models import User
from ..data.user import user_creation, user_exists


@pytest.mark.django_db
class TestSaveAction:
    """ ユーザを登録できるか検証 """

    def test_save(self):
        with user_creation() as _:
            # GIVEN
            username = 'Django'
            expected = User(username=username)
            sut = SaveAction()
            # WHEN
            actual = sut(username)
            # THEN
            assert actual == expected


@pytest.mark.django_db
class TestResultViewAction:
    """ 表示対象のユーザ情報を構築できるか検証 """

    # 表示対象のユーザをDBから取得できるか
    def test_view(self, assertion_helper):
        sut = ResultViewAction()
        expected = {
            'user': User(username='Django')
        }

        with user_exists() as user:
            # WHEN
            actual = sut(user.id)
            # THEN
            assert actual == expected
