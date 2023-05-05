import pytest
from django.core.exceptions import ValidationError
from src.simple_form.forms.validation_form import validate_password


class TestValidatePassword:
    """ パスワードのバリデーション処理を検証 """

    # バリデーションに成功するか
    @pytest.mark.parametrize(
        'value',
        ['strong_password', 'PaSsWOrd']
    )
    def test_success(self, value: str):
        sut = validate_password
        sut(value)
        assert True

    # 不正なパスワードではバリデーションエラーが送出されるか
    def test_validation_error(self):
        # GIVEN
        sut = validate_password
        invalid_password = 'password'

        # WHEN
        with pytest.raises(ValidationError):
            sut(invalid_password)
