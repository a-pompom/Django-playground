from django import forms


class ViewForm(forms.Form):
    """ 画面描画を組み立てることを責務に持つ """

    text = forms.CharField()
    checkbox = forms.MultipleChoiceField(choices=[
        ('dog', 'Dog'),
        ('cat', 'Cat'),
        ('rabbit', 'Rabbit'),
    ])
    radio = forms.ChoiceField(choices=[
        ('rice', 'Rice'),
        ('bread', 'Bread'),
    ])
    select = forms.ChoiceField(choices=[
        ('りんご', 'りんご'),
        ('ばなな', 'ばなな'),
        ('ぶどう', 'ぶどう'),
        ('らいち', 'らいち'),
    ])
