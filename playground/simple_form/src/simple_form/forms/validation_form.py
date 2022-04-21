from django import forms


class ValidationForm(forms.Form):
    """ バリデーション機能を持ったformを表現することを責務に持つ """
   
    username = forms.CharField()
    user_id = forms.CharField()
