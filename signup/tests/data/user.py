from contextlib import contextmanager
from signup.models import User


@contextmanager
def user_creation():
    """
    ユーザ登録処理のコンテキスト 後続のテストへ影響しないよう、後処理でつくったレコードを削除
    """
    try:
        yield None
    finally:
        User.objects.all().delete()


@contextmanager
def user_exists():
    """
    ユーザ表示処理のコンテキスト 後続のテストへ影響しないよう、後処理でつくったレコードを削除
    """
    user = User(username='Django')
    user.save()
    try:
        yield user
    finally:
        User.objects.all().delete()
