# 概要

簡単なform/input要素をDjangoで扱えるようにしたい。
TODO view_formのテストを書きたい。

* 画面へ渡されるformがViewFormのインスタンスか
* 結果画面へ渡すformオブジェクトへ値が設定されているか

## ゴール

form/input要素を画面へ描画し、POSTリクエストから入力を受け取れるようになることを目指す。

## 用語整理

* clean: FormのFieldの値を一定のフォーマットへ正規化すること 例えばDateFieldであれば日付の入力(文字列・dateオブジェクト)をdateオブジェクトへ統一することを指す


## request.POSTを扱いたい

まずはFormオブジェクトを使わず、requestオブジェクトから直接HTML formの入力を受け取る機能をつくってみる。
これを通じてHTTPリクエスト・Djangoのrequestオブジェクトがどのように対応しているのか理解することを目指す。

### HTTPリクエスト

まずは下図のformをsubmitしたとき、どのようなリクエストがDjangoへ送信されるのか見ておく。

![image](https://user-images.githubusercontent.com/43694794/163515030-60a071fe-a7f6-43f7-b64d-b3ee7c16b8dc.png)

```
Request URL: http://localhost:8000/form/raw_post
Request Method: POST

csrfmiddlewaretoken: ahyF7xSEWiIjKiGtFKGXScPJxx32oNtTDG5L8gzsw66h0YksI2ctLNp4NfoEtfUu
text: text here
checkbox: dog
checkbox: cat
radio: rice
select: ぶどう
```

`urls.py`に記載されたルールをもとにsubmit先のURLを組み立てていることが分かる。
また、POSTリクエストのボディは通常のPOSTリクエスト`name: value`で構築されている。

以上を踏まえた上で、Djangoで具体的にどのようにリクエストを処理しているのか見ていく。

### POSTオブジェクト

Djangoでは、HTTPリクエストを`HttpRequest`オブジェクトで表現している。

[参考](https://docs.djangoproject.com/en/4.0/ref/request-response/#httprequest-objects)

これはview関数が呼ばれるときにDjango側で引数として設定しているので、特別な処理を書くことなく参照することができる。
リクエストのPOSTボディは`request.POST`属性に設定されており、`QueryDict`と呼ばれるオブジェクトで表現される。

`QueryDict`は辞書を継承したものである。単純な辞書で表現した方がシンプルになりそうだが、チェックボックスや複数選択のセレクト要素でnameが重複していても値を保持できるようにするために
拡張されている。

[参考](https://docs.djangoproject.com/en/4.0/ref/request-response/#django.http.HttpRequest.POST)

以下にview関数からPOSTボディを取得するサンプルコードを載せておく。

```Python
def post(request: HttpRequest) -> HttpResponse:
    """
    Formオブジェクトを利用しない生のフォームへのPOSTリクエストを処理

    :param request: HttpRequest
    :return: 生のフォームによる画面を表現するHTTPレスポンス
    """
    if request.method != 'POST':
        return redirect(reverse('form:raw_get'))

    # request.POSTはQueryDictクラス型とみなされる
    # 実体はQueryDictインスタンスなので、キャストしておく
    post: QueryDict = cast(QueryDict, request.POST)

    # コンテキスト生成
    text = post.get('text', '')
    checkbox = ', '.join(post.getlist('checkbox', []))
    radio = post.get('radio', '')
    select = post.get('select', '')
    context = {
        'text': text,
        'checkbox': checkbox,
        'radio': radio,
        'select': select,
    }
    return render(request, 'raw_form_result.html', context)
```

また、POSTボディはこのままではすべて文字列で表現されるため、バリデーションや加工には向かない。
より簡潔にリクエストのPOSTボディを扱えるようにするため、Formオブジェクトを導入したい。

---

## Formオブジェクトを扱いたい

[参考](https://docs.djangoproject.com/en/4.0/topics/forms/#)

## Formオブジェクト-マッピングのみ

### Formクラスを定義したい

[参考](https://docs.djangoproject.com/en/4.0/ref/forms/fields/#built-in-field-classes)

#### Fieldのドキュメントの読み方

ここでは、各Fieldクラスのドキュメントに書かれている項目を補足しておく。

* Default widget: `as_p, as_ul`などでFormオブジェクトからHTMLを組み立てるときに利用されるHTML input要素
* Empty value: 何も入力されなかったことを表現する値を設定
* Normalizes to: リクエストでは文字列で表現されていたinput要素の入力をどんなオブジェクトへマッピングするか
* Error message keys: デフォルトのエラ〜メッセージが設定されたキー `error_messages`引数で上書きできる

項目が記述された後は、各種引数の説明へと続く。

#### CharField

文字列入力欄を表現するフィールド。

[参考](https://docs.djangoproject.com/en/4.0/ref/forms/fields/#charfield)

```Python
from django import forms

class OnlyMappingForm(forms.Form):

    text = forms.CharField()
```

#### ChoiceField

選択式の要素を表現するフィールド。

[参考](https://docs.djangoproject.com/en/4.0/ref/forms/fields/#choicefield)

choices属性へ`value, label`を表現するタプルのリストを設定しておくと、選択肢を自動的に組み立てたり、取りうる値に制約を課すことができる。

```Python
from django import forms

class OnlyMappingForm(forms.Form):

    radio = forms.ChoiceField(choices=[
        ('rice', 'Rice'),
        ('bread', 'Bread'),
    ])
```

#### MultipleChoiceField

複数選択式の要素を表現するフィールド。
選択値は文字列のリストで表現される。

[参考](https://docs.djangoproject.com/en/4.0/ref/forms/fields/#multiplechoicefield)

```Python
from django import forms

class OnlyMappingForm(forms.Form):

    checkbox = forms.MultipleChoiceField(choices=[
        ('dog', 'Dog'),
        ('cat', 'Cat'),
        ('rabbit', 'Rabbit'),
    ])
```

### POSTボディからFormクラスをインスタンス化したい

Formクラスは、イニシャライザの第一引数へ辞書オブジェクトを渡すことで、`bound form`と呼ばれる状態とすることができる。

[参考](https://docs.djangoproject.com/en/4.0/ref/forms/api/#django.forms.Form)

`bound`は束縛されたといった意味を持ち、Formオブジェクトが特定の値に束縛されたことを表現している。

これは、おそらくPythonの`bound/unbound methods`に由来していると思われる。
[bound 参考](https://www.geeksforgeeks.org/bound-unbound-and-static-methods-in-python/)

POSTボディは辞書を継承したオブジェクトなので、Formオブジェクトのイニシャライザの第一引数へ渡すことができる。
また、辞書のキーがフィールド名・辞書の値がフィールド値と対応する。フィールド名は、Formクラスの各Field属性を表現するクラス変数と対応。

```Python
def post(request: HttpRequest) -> HttpResponse:

    # request引数にはPOST属性でPOSTボディが格納されているので、そのまま渡せばよい
    form = OnlyMappingForm(request.POST)
```

### Formから値を取得したい

Formの値は、Formオブジェクトの`cleaned_data`属性と呼ばれる辞書オブジェクトへ保存されている。
ここでのcleanedは、値が一定のフォーマットに基づいて正規化されていることを指す。

[参考](https://docs.djangoproject.com/en/4.0/ref/forms/api/#accessing-clean-data)

```Python
def post(request: HttpRequest) -> HttpResponse:
    
    form = OnlyMappingForm(request.POST)
    # 今回はバリデーションを扱わないので触れないでおく
    form.is_valid()

    # Formオブジェクトのcleaned_data属性から各フィールドの値へアクセス
    text = form.cleaned_data.get('text', '')
    checkbox = ', '.join(form.cleaned_data.get('checkbox', []))
    radio = form.cleaned_data.get('radio', '')
    select = form.cleaned_data.get('select', '')
```

このように記述することで、生のHTML form・`requset.POST`と同じように入力要素を読み出すことができた。


## Formオブジェクト-画面描画

今度は、入力・結果画面をFormオブジェクトから描画してみる。 描画には色々なパターンがあるが、今回は汎用性の高い手動描画を試してみる。

### 入力画面を描画したい

まずは、入力画面をFormオブジェクトをベースに組み立ててみる。
Formオブジェクトの属性へテンプレートからアクセスするときは、`__getitem__()`が呼ばれる。

[参考](https://docs.djangoproject.com/en/4.0/ref/templates/language/#variables)

すると、BoundFieldオブジェクトが得られる。

[BoundField参考](https://docs.djangoproject.com/en/4.0/ref/forms/api/#more-granular-output)

BoundFieldオブジェクトを介してname属性やFieldオブジェクトに設定したchoices引数などにアクセスすることができる。

[BoundFieldの各属性へのアクセス方法参考](https://docs.djangoproject.com/en/4.0/topics/forms/#looping-over-the-form-s-fields)

例えば単純なテキスト入力であれば、name属性をFormオブジェクトの属性名に、BoundFieldを介して設定することができる。

```HTML
<label for="text">Text</label>
<input
    type="text"
    name="{{ form.text.name }}"
    placeholder="text"
    id="text">
```

また、FormオブジェクトのField属性は、BoundFieldにてCompositionにより所有されているので、`field属性`からアクセスすることができる。

```HTML
<p>Radio</p>
{% for name, value in form.radio.field.choices %}
    <label for="radio{{ value }}">{{ value }}</label>
    <input
        type="radio"
        name="{{ form.radio.name }}"
        value="{{ value }}"
        id="radio{{ value }}">
{% endfor %}
```

受け取った後の挙動は単純なマッピングと同じなので省略。

### 結果画面を描画したい

コンテキストにFormオブジェクトだけを設定して結果画面を描画してみる。
※ 本来はデータベースへ保存してリダイレクトしたり、遷移先の画面で改めて取得すべきだが、今回は実験用プログラムなので直接描画する。

```HTML
<h4>Text</h4>
<p>{{ form.text.value }}</p>

<hr>

<h4>CheckBox</h4>
{% for value in form.checkbox.value %}
<p>{{ value }}</p>
{% endfor %}

<hr>

<h4>Radio</h4>
<p>{{ form.radio.value }}</p>

<hr>

<h4>Select</h4>
<p>{{ form.select.value }}</p>
```

基本的には入力画面と同様、BoundFieldを介してアクセス。
ただし、チェックボックスのように、同一のname属性で複数の値を保持するものはループを通じて各値を取り出す。



## Formオブジェクト-バリデーション