from django import forms


class OnlyMappingForm(forms.Form):
    """ POSTボディのマッピングのみを責務に持つ """

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
