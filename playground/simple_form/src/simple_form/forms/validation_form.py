from django import forms
from django.core import validators
from django.core.exceptions import ValidationError


def validate_password(value: str):
    """
    パスワードをバリデーション
    
    :param value: パスワードの入力値
    """
    # 擬似的にバリデーションエラーを送出するために不正なパスワードを仮で設定
    invalid_password = 'password'

    if value == invalid_password:
        raise ValidationError('そのパスワードは使えません。')


class ValidationForm(forms.Form):
    """ バリデーション機能を持ったformを表現することを責務に持つ """

    username = forms.CharField(
        validators=[validators.RegexValidator(validators.slug_re, 'ユーザ名はSlug形式で入力してください。')],
        error_messages={
            'required': 'ユーザ名を入力してください。'
        }
    )
    password = forms.CharField(
        validators=[validate_password],
        error_messages={
            'required': 'パスワードを入力してください。'
        }
    )
