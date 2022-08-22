from typing import TypedDict
from ..models import User


class SaveAction:
    """ ユーザ登録処理を責務に持つ """

    def __call__(self, username: str) -> User:
        """
        ユーザ情報をDBへ登録
        :param username: 登録ユーザのユーザ名
        :return 登録されたユーザModel
        """
        user = User(username=username)
        user.save()

        return user


class TypeContext(TypedDict):
    """ ユーザ登録結果画面のコンテキストを表現することを責務に持つ """
    user: User


class ResultViewAction:
    """ ユーザ登録結果画面のコンテキストを組み立てることを責務に持つ """

    def __call__(self, user_id: int) -> TypeContext:
        """
        ユーザ情報をコンテキストとして組み立て
        :param user_id 表示対象ユーザID
        :return ユーザ情報を含むコンテキスト
        """
        user = User.objects.get(id=user_id)

        return {
            'user': user
        }
