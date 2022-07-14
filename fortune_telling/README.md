# 概要

Djangoでランダムに運勢を表示するおみくじアプリをつくってみます。

## ゴール

Djangoのテンプレート・コンテキストを理解し、おみくじの結果を表示するアプリケーションをつくることを目指します。

## 目次

[toc]

## 用語整理

* テンプレート: HTTPレスポンスのボディとなるHTMLを生成するためのひな形
* コンテキスト: テンプレートから動的なHTMLを組み立てるときに参照される辞書オブジェクト
* 逆引き: 名前付きURLからviewと対応するURLを得ること
* 名前付きURL: 逆引きによって参照される`app名:viewの識別子`形式の文字列

## つくりたいもの

アプリケーションの全体像を知るため、これから何をつくるのか見ておきます。つくりたいのは、「おみくじ」ボタンをクリックするとランダムな運勢を表示してくれる機能です。具体的なイメージは下図の通りです。

![image](https://user-images.githubusercontent.com/43694794/151642602-98aa7f58-a80f-4727-9867-9cab446367f0.png)
図1: おみくじトップ画面

![image](https://user-images.githubusercontent.com/43694794/151642612-d2e737e8-7344-4fae-83c5-fcb229f9ac28.png)
図2: おみくじ結果画面

機能に物足りなさはありますが、動的にHTMLを表示したり、画面を切り替えたりと、いくつかのDjangoの新しい知識を身につけることができます。
どのようにDjangoでおみくじアプリケーションをつくっていくのか、一歩ずつ見ていきましょう。


## 前準備-復習

Hello Worldアプリケーションでも触れましたが、Djangoでアプリケーションを開発するときは毎回、土台としてプロジェクト・appをつくります。ですので、慣れるまでは流れを復習しながら進めていきます。

### プロジェクトをつくる

まずはアプリケーションそのものと付随する設定値などを持つプロジェクトをつくります。

```bash
# Hello Worldとは別のsrcディレクトリで実行してください。
# ex: /fortune_telling/src
$ django-admin startproject config .
# つくられたファイルを表示
$ tree
.
├── __init__.py
├── config
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── manage.py
```

### appをつくる

続いて、おみくじを表現するappをつくります。名前は`fortune_telling`としておきます。

```bash
$ django-admin startapp fortune_telling

# つくられたファイル・ディレクトリを確認
$ tree
.
├── __init__.py
├── config
│         ├── __init__.py
│         ├── asgi.py
│         ├── settings.py
│         ├── urls.py
│         └── wsgi.py
├── fortune_telling
│         ├── __init__.py
│         ├── admin.py
│         ├── apps.py
│         ├── migrations
│         │    └── __init__.py
│         ├── models.py
│         ├── tests.py
│         └── raw.py
└── manage.py
```

Hello Worldアプリケーションと同じような構成をつくり出すことができました。

#### INSTALLED_APPSへ追記

最後に、新しくつくったappをDjangoへ認識させるために、settings.pyの`INSTALLED_APPS`へ追記します。記述形式はPythonのimport文と同じです。

```Python
# src/config/settings.py
# 中略...
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 追記
    'fortune_telling.apps.FortuneTellingConfig',
]
```

---

準備が整ったので、ここからはおみくじを引くためのトップ画面・おみくじの結果を表示するための画面を実装していきます。

## トップ画面

まずは入り口となる画面から始めます。別画面へのリンクまで実装しようと思うと考えることが多くなってしまうので、とりあえず画面を表示させることだけに集中します。

### テンプレート

Hello Worldアプリケーションでは、HttpResponseオブジェクトのイニシャライザへ文字列を渡すことで、HTTPレスポンスのボディを組み立てていました。単純に考えれば、トップ画面を表現するHTML文字列を同じように記述すれば、やりたいことは実現できそうです。

```Python
# 文字列でHTMLを組み立てるイメージ
from django.http import HttpRequest, HttpResponse

def sample(request: HttpRequest) -> HttpResponse:
    return HttpResponse(
        '\n'.join(
            (
                '<!DOCTYPE html>'
                '<head>'
                '...'
            )
        )
    )
```

しかし、これでは見た目を変えるためにPythonファイルをメンテナンスすることになり、表示とロジックが密に結びついてしまいます。そもそも補完や自動生成など、エディタの恩恵を受けられなくなり、開発効率ががくっと下がってしまいそうです。

ここで、表示したい画面のひな形となるHTMLファイルを用意しておき、おみくじの結果・登録されたユーザ名など、動的に描画したいものだけを個別に埋め込めるようになればうまくいきそうです。
Djangoはこういった課題を解決するために、`テンプレート`という仕組みを提供してくれています。

---

細かい使い方は後々見ていくので、この場では、テンプレートを使っていけば状態に応じて変化するHTML文字列がつくれるんだな〜、ということを覚えておきましょう。
[参考](https://docs.djangoproject.com/en/4.0/topics/templates/)

#### 置き場所

何はともあれ、画面を表現するHTMLファイルを用意した方が良さそうだということが分かりました。ですが、先ほどつくったプロジェクトディレクトリやappにはテンプレートを置くのに良さそうな場所が見当たりません。どこへ配置するか考えてみます。
先に結論を書くと、appと同様にsrcディレクトリ直下へ置くことにします。具体的なディレクトリ構造は下図を参考にしてください。

![image](https://user-images.githubusercontent.com/43694794/151650101-0bbd94c5-75fe-4815-aaf6-6017d6bdb4fd.png)
図3: テンプレートを含めたディレクトリ構成

こうすることで、Djangoがテンプレートを探しにいくときのルールをシンプルにすることができます。具体的なルールは後ほど設定値とあわせて見ていきます。

#### HTML

置き場所が決まったので、templatesディレクトリ・トップ画面を表現するHTMLファイルをつくっていきます。今はまだDjangoが関わるところもないので、とりあえずつくって置いておきましょう。
※ スタイルにはtailwindcssを採用していますが、本記事はスタイルの解説が目的ではないので、説明を割愛します。

```HTML
<!-- src/templates/index.html -->
<!DOCTYPE html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, height=device-height, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=M+PLUS+1p:wght@500&display=swap" rel="stylesheet">
    <title>おみくじ</title>
</head>
<style>
    body {
        font-family: 'M PLUS 1p', sans-serif;
    }
</style>
<body class="overflow-hidden w-full h-screen">
<div class="grid place-content-center h-full bg-white">

    <h2 class="text-6xl tracking-wider text-center text-slate-500">
        今日の運勢を占います。
    </h2>
    <button class="p-3 mx-auto mt-24 w-3/6 text-4xl tracking-wider text-center text-white bg-sky-300 rounded-3xl hover:bg-sky-500">
        <a href="#">おみくじ!!</a>
    </button>
</div>
</body>
</html>
```

#### テンプレートの設定

さて、テンプレートからHTML文字列を組み立てる処理は、Djangoへ任せることにしたいです。そのためには、新しくつくったtemplatesディレクトリをDjangoに伝えなくてはなりません。こういった設定は、`config/settings.py`へ記述していきます。まずは設定内容を見てみましょう。

```Python
# src/config/settings.py
from pathlib import Path

# BASE_DIRは、srcディレクトリを指す
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# 中略...

# テンプレート関連の設定
TEMPLATES = [
    {
        # どんな仕組みでテンプレートからHTMLを組み立てるか
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # テンプレートファイル探索パス
        # 下の記述は、src/templatesとなる
        'DIRS': [BASE_DIR / 'templates'],
        
        # テンプレートファイルを探索するとき、app内部のディレクトリを対象に含めるか
        # 今回はapp以下へテンプレートファイルを配置することはないので、無効にしておく
        'APP_DIRS': False,
        # テンプレートからHTMLを組み立てるときのオプション
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

見るべきは、`BASE_DIR`と`TEMPLATES`です。文字通り、Djangoアプリケーションにおいて基準となるディレクトリと、テンプレートの設定値が書かれています。
そして、今回最も重要な設定値は`DIRS`です。DjangoがテンプレートとなるHTMLを探しに行くとき、通常はここに書かれたパスを起点とします。ですので、新しくつくった`src/templates`を追記することで、Djangoが探しに行けるようにしておきます。
[参考](https://docs.djangoproject.com/en/4.0/ref/settings/#dirs)

※ Django3.1からは、ディレクトリ名を書くときに参照されるライブラリがosからpathlibへ変更されているので、過去のバージョンのDjangoに触れてきた方は注意が必要です。
[参考](https://docs.djangoproject.com/en/4.0/releases/3.1/#miscellaneous)


### view

テンプレートが扱えるようになったので、テンプレートをもとにHTTPレスポンスを組み立てるviewをつくってみます。基本的な構造はHello Worldと同じで、HTTPレスポンスのボディをテンプレートからつくり上げることだけが異なります。これはコードでも表現されているので、実際に見てみましょう。

```Python
# src/fortune_telling/views.py
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string


def index(request: HttpRequest) -> HttpResponse:
    """
    トップ画面表示

    :param request: HTTPリクエスト
    :return: トップ画面をボディに持つHTTPレスポンス
    """
    return HttpResponse(render_to_string('index.html'))
```

重要なのは、`render_to_string()`です。まずは書式を確認しておきます。
[参考](https://docs.djangoproject.com/en/4.0/topics/templates/#django.template.loader.render_to_string)

> 書式: `render_to_string(template_name, context=None, request=None, using=None)`

必須となる`template_name`のみ指定しています。これは、文字通り利用するテンプレート名で、先ほど見た`DIRS`へ追記したディレクトリを起点としたパスを記述しています。 つまり、`DIRS`が`src/templates`であることから、指定されたindex.htmlファイルは、`src/templates/index.html`を対象に探索されます。
このように書くことで、Hello Worldアプリケーションでは単純な文字列だったHTTPレスポンスのボディを、HTMLファイルのテンプレートから組み立てられるようになります。

### URLconf

続いて、URLとviewを対応づけるためにURLconfを書いていきます。手順はHello Worldと同じなので、出来上がったものを見ておきましょう。

```Python
# src/config/urls.py
from django.contrib import admin
from django.urls import path, include


# config以下のURLconfは最初に参照される
# パスが/fortune/で始まるURLは、fortune_telling appのURLconfが参照される
urlpatterns = [
    path('admin/', admin.site.urls),
    path('fortune/', include('fortune_telling.urls')),
]

```

```Python
# src/fortune_telling/urls.py
from django.urls import path

from .views import index

# パスが/fortune/のURLと、views.pyのindex関数を対応づける
urlpatterns = [
    path('', index),
]
```

### 画面表示

これでDjangoがテンプレートをもとにトップ画面を表示させるための準備が整いました。本当に動いてくれるのか、開発サーバで確かめておきましょう。

```bash
$ python manage.py runserver
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).

# 警告はDBを扱うようになるまでは触れないでおきます
You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.
Django version 4.0.1, using settings 'config.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

`http://localhost:8000/fortune/`へアクセスし、最初に見た画面が表示されていれば成功です。

## おみくじ結果画面`

トップ画面が出来上がったので、続けておみくじを引いた結果を表示する画面をつくっていきます。毎回変化する運勢をどのように実装・表示するのか、考えていきましょう。

### テンプレート

トップ画面と同じように、まずはテンプレートとなるHTMLからつくっていきます。

```HTML
<!-- src/templates/fortune.html -->
<!DOCTYPE html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, height=device-height, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=M+PLUS+1p:wght@500&display=swap" rel="stylesheet">
    <title>おみくじ結果</title>
</head>
<style>
    body {
        font-family: 'M PLUS 1p', sans-serif;
    }
</style>
<body class="overflow-hidden w-full h-screen">
<div class="grid place-content-center h-full bg-white">

    <!-- おみくじの結果を表示する箇所でDjango template languageを記述 -->
    <h2 class="text-6xl tracking-wider text-center text-slate-500">
        今日の運勢は、{{ fortune }}です!!
    </h2>
</div>
</body>
</html>
```

`{{ fortune }}`という見慣れない記述があります。これは、[Django template language](https://docs.djangoproject.com/en/4.0/ref/templates/language/)と呼ばれるテンプレート言語の記法の1つです。
Djangoは上のような記法や、後述するコンテキストというオブジェクトをもとに、動的なHTMLをつくり出すことができます。ここでは、Djangoはテンプレートに特別な記法を含めてレンダリングすると、動的にHTMLをつくってくれるんだな、ということを覚えておきましょう。

#### `{{ variable }}`

具体的な記法にも触れておきましょう。変数名が`{{`と`}}`の間に記述されていると、記法を含めて変数の値で置き換えられます。イメージをコードで表現すると、以下のようになります。

```Python
context = {
    'message': 'Hello, DTL!!'
}
```

```HTML
<!-- 置き換え前 -->
<h1>{{ message }}</h1>
<!-- 置き換え後 -->
<h1>Hello, DTL!!</h1>
```

記法がDjango template languageで解釈されると、変数contextにより置き換えられ、HTTPレスポンスのボディとすることができるような表現が手に入ります。
[参考](https://docs.djangoproject.com/en/4.0/ref/templates/language/#variables)

### view

テンプレートが出来上がったので、続けてviewへ取り掛かります。viewでは、先ほど少し触れたコンテキストオブジェクトをつくっていることがポイントです。イメージを掴むためにまずはコードを見てみましょう。

```Python
# src/fortune_telling/raw.py
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string

# テストコードでランダム関数をモック化できるよう、モジュールのみimport
from . import fortune as fortune_module
# 中略...
def fortune_telling(request: HttpRequest) -> HttpResponse:
    """
    おみくじ結果画面表示

    :param request: HTTPリクエスト
    :return: おみくじ結果画面をボディに持つHTTPレスポンス
    """
    # おみくじの結果を関数より取得
    fortune = fortune_module.tell_fortune()
    # テンプレートからHTMLを生成するときに参照されるコンテキスト
    context = {
        'fortune': fortune
    }

    # コンテキストをもとにテンプレートからHTML文字列を生成した結果をHTTPレスポンスのボディとする
    return HttpResponse(render_to_string('fortune.html', context=context))
```

注目すべきは、辞書で定義されたコンテキストオブジェクトです。これは、`render_to_string()`では、レンダリングのためのテンプレートのコンテキストであると説明されています。
[参考](https://docs.djangoproject.com/en/4.0/topics/templates/#django.template.loader.render_to_string)

何やら難しそうな表現ですが、Django template languageが記法をもとにHTMLを組み立てるときに変数を探しに行く場所がコンテキストだ、と捉えると理解しやすいかもしれません。

#### おみくじ関数

運勢を導き出す関数もさらっと覗いておきます。単にランダム関数をもとに`小吉・中吉・大吉`いずれかの文字列を返却しているだけなので、特に難しいところはないかと思います。

```Python
# src/fortune_telling/fortune.py
import random

FORTUNE_CANDIDATE = ('小吉', '中吉', '大吉')


def tell_fortune() -> str:
    """
    運勢の文字列を生成

    :return: 運勢を表す文字列
    """
    fortune = random.randint(0, len(FORTUNE_CANDIDATE) - 1)
    return FORTUNE_CANDIDATE[fortune]

```

#### 補足: コンテキストという言葉

コンテキストはDjangoに限らずさまざまな場面で使われる表現ではありますが、いまいち意味がイメージしづらいように思えます。大事な要素なので、ここで少し掘り下げておきましょう。
コンテキストには文脈・環境といった意味があります。コンピュータ関連では、同じ状況を再現するためのデータといった意味で使われることもあります。コンテキストスイッチで検索すると、理解が深まるかもしれません。
[参考](https://en.wikipedia.org/wiki/Context_(computing))

Djangoに話を戻すと、コンテキストは、あるリクエストから対応するレスポンスを生成するためのデータ(環境)と捉えることができます。テンプレートとなるHTMLをベースにレスポンスを組み立てるのであれば、同じコンテキストからは同じレスポンスが生まれるはずです。
このように、実際の用途だけでなく、言葉の意味とも照らし合わせながら考えると、概念の理解が進んでいくはずです。

#### 補足: なぜapp内部では相対importで記述するのか

今まで`INSTALLED_APPS`や設定ファイルでは、絶対importでモジュールを読み込んでいました(例: `fortune_telling.apps.FortuneTellingConfig`)。そう考えると、viewやURLconfから同階層のファイルをimportするときも、`fortune_telling.fortune`のように記述するのが自然なように思えます。
なぜ書き方が統一されていないのでしょうか。

これは、app内部ではappの名前を書かないことで、再利用性を高めるためです。Djangoはappを再利用可能なものとして定義しているので、相対importによりappの名前に依存しないようにしています。
[参考](https://learndjango.com/tutorials/django-best-practices-imports)

---

### URLconf

viewが完成したので、URLconfにも追記しておきます。トップ画面と同じようにURLとview関数を対応づけておきます。

```Python
# src/fortune_telling/urls.py
from django.urls import path

from .views import index, fortune_telling

# パスが/fortune/fortune_telling/のURLと、views.pyのfortune_telling関数を対応づける
urlpatterns = [
    path('', index),
    path('fortune_telling/', fortune_telling)
]
```

### 動作確認

おみくじ結果画面も出来上がったので、開発サーバを動かしてみましょう。

```bash
$ python manage.py runserver
# 出力は省略
```

`http://localhost:8000/fortune/fortune_telling/`へアクセスし、アクセスする度に変わる運勢が表示されていれば成功です。


## リンクで繋げる

最後の仕上げとして、トップ画面からおみくじを引けるようにしておきます。

おみくじの結果画面は、`http://localhost:8000/fortune/fortune_telling`から見ることができました。ということは、2つの画面を繋げるにはトップ画面へ`<a href="/fortune/fortune_telling">...</a>`のような記述を追加すれば良さそうです。
ですが、DjangoではURLに依存(べた書き)しない別の方法が推奨されています。それは逆引きと呼ばれる、名前付きURLなるものから対応するURLを得ることです。
[参考](https://docs.djangoproject.com/en/4.0/topics/http/urls/#reverse-resolution-of-urls)

これだけではイメージが掴みづらいので、テンプレート・URLconfでどのように書かれるのか、具体例から見ていくことにします。

```Python
# src/fortune_telling/urls.py
from django.urls import path

from .views import index, fortune_telling

# appの名前空間
# appを識別するための名称を指定
app_name = 'おみくじ'
urlpatterns = [
    # name引数がviewの識別子となる
    path('', index, name='トップ'),
    path('fortune_telling/', fortune_telling, name='結果')
]
```

```HTML
<!-- src/templates/index.html -->
<!-- おみくじボタンと対応するaタグのhref属性を変更-->
<a href="{% url 'おみくじ:結果' %}">おみくじ!!</a>
```

URLconfでは、appの名前空間や、viewの識別子に関する情報が増えました。更に、テンプレートでは、新たにつくられた名前付きURLをよしなに参照しているような記述が追加されています。
中々に複雑なものに見えますが、`Djangoがどのようにviewと対応するURLを得ようとしているのか`理解することを目指して少しずつ見ていきましょう。

### appの名前空間

まずはURLconfから読み解いていきます。app_name属性は`application namespaces`とも呼ばれ、逆引きでURLを得るときのappの識別子として扱われます。
つまり今回の例に照らし合わせると、`おみくじ`という名前と対応するappはfortune_tellingだということをapp_name属性を通じて表現することができます。

### viewの識別子

続いて、path関数のnameキーワード引数も見ておきます。これは、個々のview関数へ指定することができ、view関数の識別子として扱われます。

また、名前空間や識別子にはURLに利用できる文字に限定するといった制約もないので、例のように日本語を指定することもできます。
[参考](https://docs.djangoproject.com/en/4.0/topics/http/urls/#url-namespaces-and-included-urlconfs)

#### 名前付きURL

さて、ここでappの名前空間とviewの識別子が逆引き・名前付きURLとどのように関わるのか整理しておきましょう。
後ほどテンプレートでも見ていきますが、`appの名前空間:viewの識別子`で記述された文字列こそ、名前付きURLとなります。そして、名前付きURLから対応するURLを得ることは、逆引きと表現されます。

まとめると、urls.pyへappの名前空間(app_name)・viewの識別子(path関数のnameキーワード引数)を追加することで、紐づくview関数を名前付きURLで表せるようになりました。名前付きURLは何らかの手段で逆引きされることで、実際にユーザがアクセスできるURLへと変換されます。
[参考](https://docs.djangoproject.com/en/4.0/topics/http/urls/#url-namespaces)

### urlタグ

続いて、テンプレートへ加わった記法を見てみます。
`{% tag %}`で書かれたものはタグと呼ばれています。if文っぽいもの・for文っぽいものや、今回のようにURL文字列を出力するものといったように、様々な用途で使われます。
つまり、タグを記述することでロジックを書いたり、何らかのオブジェクトを画面向けに加工したりと、テンプレートを拡張できるようになります。

[参考](https://docs.djangoproject.com/en/4.0/ref/templates/language/#tags)

---

話をurlタグへ戻します。urlタグは、ユーザに見える形のURLを便利につくり出すためのものです。
`{% url 'URL pattern name' %}`のように名前付きURLを指定すると、対応するviewを呼び出すためのURL文字列が出力として得られます。具体的な例は以下のようになります。

```HTML
<!-- テンプレートの記述 -->
<a href="{% url 'おみくじ:結果' %}">おみくじ!!</a>
<!-- ユーザが目にするHTML -->
<a href="/fortune/fortune_telling/">おみくじ!!</a>
```

[参考](https://docs.djangoproject.com/en/4.0/ref/templates/builtins/#url)

### 画面表示

さて、これで画面が繋がったはずです。`http://localhost:8000/fortune/`へアクセスし、「おみくじ」ボタンを押してみましょう。
結果画面へ移動し、運勢が表示されていれば成功です。

#### 補足: なぜ逆引きという名前なのか

これまで見てきた、名前付きURLから対応するURLを得る手法は、なぜ逆引きと名付けられたのでしょうか。少し考えてみましょう。
通常、Djangoでリクエストからレスポンスを得るまでには、「URL→view→HTTPレスポンス」といった順に処理が進んでいきます。
一方、逆引きでは、「名前付きURL→URL」といった順に処理されます。これはURLを始点にHTTPレスポンスを得る上記の処理とは逆に、URLを得ることが終点となっています。

このように通常の処理の起点となるものを出力とすることから、逆引きと銘打たれたと考えられます。

#### 補足: 名前付きURLという表現

名前付きURLという表現について、補足しておかなければなりません。これは実はDjangoで公式に呼ばれているものではなく、便宜上名前付きURLと表現しておりました。
というのも、`appの名前空間:viewの識別子`で表される文字列は、公式で明確な名前がつけられていません。かといって公式の呼び名が無いものを長々と書き表すのも冗長な気がします。

よって、Djangoの記事では、上述の文字列を、公式の表現で最も近いと思われる名前付きURL(named URL)と呼ぶことにします。

## まとめ

Djangoのテンプレート・コンテキストを駆使して、おみくじアプリをつくってきました。Django特有のルールが徐々に増えて少しずつ複雑になってきましたが、`なぜこの記述が必要か`を意識しながら身につけていきましょう。
