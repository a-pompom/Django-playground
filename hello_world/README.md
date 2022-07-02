# 概要

Djangoへ入門する始めの一歩として、Hello Worldアプリケーションをつくってみます。

## ゴール

Djangoの基本的な処理に関わるモジュールの役割を知り、文字列Hello Worldを返却するHTTPレスポンスをつくり出すことを目指します。

## 目次

[toc]

## 用語整理

* プロジェクト: アプリケーションおよび設定を表現するPythonパッケージ
* アプリケーション(app): 特定の機能を持つWebアプリケーション プロジェクトは、複数のアプリケーションを内包する
* 管理コマンド: `django-admin`や`manage.py`で実行されるコマンド プロジェクトやアプリケーションに関わる操作を担う


## Hello Worldまでの道のり

Hello Worldを題材に、Djangoでアプリケーションをつくるときの大まかな流れを見ていきます。入門の一歩目とはいえ、Django特有のものをいくつか扱っていきます。ですので、迷子にならないようまずはざっくりと全体像を掴むことから始めます。

### 処理フロー

最初に、これから何をつくるのか俯瞰しておきます。

* アプリケーションの骨組みとなるプロジェクト
* アプリケーションの個々の機能を表現するapp
* HTTPリクエストからHTTPレスポンスを組み立てるview
* URLと結びつくviewを呼び出すためのURLconf

それぞれ具体的なイメージをもう少し掘り下げてみましょう。

#### プロジェクトとアプリケーション

最初に、アプリケーションそのものと、付随する設定値を表現するPythonパッケージをつくります。Djangoでは、これをプロジェクトと呼びます。
続いて、プロジェクトの中にアプリケーションを動かすのに必要なモジュール群をつくっていきます。これはアプリケーションと呼ばれます。
ここで、つくる対象のアプリケーションと、Djangoの用語としてのアプリケーションが混ざってしまいそうです。後者のアプリケーションは公式でappと記述されているようなので、これからDjangoの用語としてのアプリケーションは、appと表現します。

簡単にまとめると、Djangoのアプリケーション開発は、プロジェクトという大枠・少し小さくなったappという骨組みへ機能を肉付けすることで進めていきます。

#### viewとURLconf

Hello Worldで求められる機能は、特定のURLへリクエストが送信されたとき、Hello Worldメッセージをレスポンスとして返却することです。これをDjangoでは、view・URLconfと呼ばれるモジュールで実現します。
viewはHTTPリクエストを入力に、HTTPレスポンスを出力する役割を担います。Djangoでは関数やクラスで表現されます。
そしてURLconfは、URLと対応するviewをマッピングする役割を担います。DjangoではPythonモジュールで表現されます。

---

DjangoでHello Worldアプリケーションをつくるときに必要な枠組み・モジュールを簡単に見てきました。まだイメージが掴めていなくても、手を動かしていけば徐々に馴染んでくるはずです。一歩ずつ組み上げていきましょう。


## 実装

実際にコマンドを実行したり、コードを書いていきます。これまで見てきたイメージがどのように形づくられるのか、順にたどっていくことにします。

### プロジェクト

早速プロジェクトをつくることから始めましょう。プロジェクトはアプリケーションと付随する設定値などを含むPythonパッケージで、`django-admin startproject`コマンドでつくることができます。コマンドの書式は下記の通りです。
[参考](https://docs.djangoproject.com/en/4.0/ref/django-admin/#startproject )

> 記法: `django-admin startproject name [directory]`

nameオプションにはプロジェクト名を、directoryオプションにはプロジェクトとしたいディレクトリを指定します。指定方法によって少し挙動が異なりますが、directoryオプションを毎回指定すればシンプルに考えることができます。
具体的には、指定されたディレクトリへnameオプションと対応する名前のPythonパッケージ(設定ディレクトリ)・manage.pyと呼ばれるファイルをつくります。このとき、directoryオプションに指定したディレクトリがプロジェクトの役割を持つようになります。。
nameオプションは設定値を持つことが分かりやすくなるよう`config`・directoryオプションは余計なディレクトリが増えないよう`.`(カレントディレクトリ)を記述してみます。オプションが定まったので、プロジェクトをつくってみます。

```bash
# プロジェクトをつくる
$ django-admin startproject config .
# つくられたファイルを表示
$ tree
# この配下すべてがプロジェクト
.
├── __init__.py
# 設定値を表現するパッケージ
├── config
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── manage.py
```

コマンドを実行したディレクトリへ設定値を表現するconfigパッケージと、管理コマンドを実行するためのmanage.pyができあがりました。
この機会に全体の概要を押さえておきましょう。

#### __init__.py

プロジェクトのディレクトリがPythonパッケージであることを示すためのモジュールです。

#### asgi.py, wsgi.py

Pythonにおいて、一定のルールでHTTPリクエスト・レスポンスを処理できるようにするためのモジュールです。Webアプリケーションを公開するときまでは意識しなくても大丈夫です。

#### settings.py

アプリケーション全体の設定値を記述したモジュールです。細かな設定値は後々見ていくことにします。

#### urls.py

URLconfと呼ばれる、URLとviewを対応づけるためのモジュールです。

#### manage.py

Webサーバを起動したり、データベースをModelと同期したりと、開発においてよく使う操作をまとめたモジュールです。

---

`django-admin startproject config .`コマンドからプロジェクトをつくることで、どこに何があるのか明確なルールを定めることができました。
以降の実践でも構造を固定できるよう、上記のコマンドからプロジェクトを組み立てていきましょう。


### アプリケーション(app)

続いて、Hello Worldの機能を実現するappをつくります。appは`django-admin startapp`コマンドによりつくられます。
[参考](https://docs.djangoproject.com/en/4.0/ref/django-admin/#startapp)

> 記法: `django-admin startapp name [directory]`

nameオプションで指定された名称のPythonパッケージがappとしてつくられます。directoryオプションを省略すると現在のディレクトリへつくられますが、別のディレクトリを指定するケースは少ないので、省略して問題ないかと思います。

```bash
# appをつくる
$ django-admin startapp hello_world
# ディレクトリ構造を表示
$ tree ./hello_world 
./hello_world
├── __init__.py
├── admin.py
├── apps.py
├── migrations
│    └── __init__.py
├── models.py
├── tests.py
└── raw.py
```

プロジェクトと同じように、たくさんのファイルができあがりました。それぞれ簡単に見ていきましょう。また、中には機能がイメージしづらいモジュールもありますが、後々触れていく中で理解すれば問題ありませんので、こんなのがあるんだ〜ぐらいのイメージで大丈夫です。

#### __init__.py

ディレクトリがPythonパッケージであることを示すモジュールです。

#### admin.py

管理サイトと呼ばれる機能でModelを扱うためのモジュールです。

#### apps.py

appのメタデータを記述するモジュールです。

#### migrations

Modelをもとにしたデータベースへの変更内容を記録したディレクトリです。

#### models.py

データベースのテーブルと対応するオブジェクトを記述するモジュールです。

#### tests.py

ユニットテストを記述するモジュールです。ユニットテストは別のディレクトリ・モジュールで記述するため、このファイルを触ることはありません。

#### views.py

HTTPリクエストからHTTPレスポンスをつくり出すviewを記述するモジュールです。

---

### 開発サーバ

プロジェクト・appをつくることで、たくさんのモジュールができあがりました。1つ1つを細かく見ていては迷子になってしまうので、ひとまず本筋のWebアプリケーションへ目を向けることにします。
ということで、定番の開発サーバをお試しで動かしてみましょう。やり方はフレームワークによってまちまちですが、Djangoではコマンド1つでさくっと動かすことができます。まずは動かした様子を見てみます。

```bash
$ python manage.py runserver
# 出力
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).

# 警告 今は気にしなくてOK
You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.

Run 'python manage.py migrate' to apply them.
January 15, 2022 - 14:47:17
Django version 4.0.1, using settings 'config.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

警告が表示されましたが、これはデータベースを扱うようになったときに解消していきます。
ここで実行したコマンドは、言葉で表現すると`引数にrunserverを指定したmanage.pyをPythonインタプリタで実行した`といった意味になります。つまり、`manage.py`が受け取ったrunserver引数を受けて開発サーバを起動してくれたことを意味します。
[参考](https://docs.djangoproject.com/en/4.0/intro/tutorial01/#the-development-server)

出力の末尾に表示されている通り、`http://127.0.0.1:8000/`へアクセスすることで、開発サーバが動いているか見ることができます。

![image](https://user-images.githubusercontent.com/43694794/149648997-2c226fa1-a7f6-4e1b-b6c9-8d8f943e2de4.png)

無事に確認できました。開発サーバはこれから何度も動かすことになるので、起動から停止までの流れを押さえておきましょう。
Ctrl+Cで止めることができるので、よきところでHello Worldを試すまでは停止させておきます。

### appの登録

開発サーバを試すことができたので次はアプリケーションを開発...といきたいところですが、最後にもう1つだけやることがあります。
新しくつくったHello World appをDjangoに知ってもらいます。今は設定しなくても動くには動きますが、Modelを扱うときは必ず設定することなるので、今のうちから習慣づけてしまいましょう。

`config/settings.py`で項目`INSTALLED_APPS`を探します。文字列のリストで表現されているので、末尾へ`hello_world.apps.HelloWorldConfig,`を追記します。こうすることで、Djangoがそれぞれのappを探しに行くとき、今回新しくつくったHello World appを見つけられるようになります。

```bash
# config/settings.py
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'hello_world.apps.HelloWorldConfig',
]
```

また、この記述はimport文の形式であることから、hello_worldパッケージのappsモジュールのHelloWorldConfigクラスを読み込んでいることを意味しています。

---

ようやくアプリケーションをつくる準備が整いました。最初は随分と長い手順に感じるかもしれませんが、経験を重ねていけば、手に馴染んでくるはずです。

### view

まずはHTTPリクエストからHTTPレスポンスを組み立てるメインの処理を担うviewをつくります。こう書くと難しそうですが、Djangoの枠組みに従うとシンプルに書くことができます。ひとまずできあがったコードを見てみましょう。


```Python
# hello_world/raw.py
from django.http import HttpRequest, HttpResponse


def hello_world(request: HttpRequest) -> HttpResponse:
    """
    Hello World文字列をレスポンスとして生成

    :param request: HTTPリクエスト
    :return: Hello World文字列をボディとするHTTPレスポンス
    """
    return HttpResponse('Hello World')
```

関数を眺めていると、viewの役割と対応していることが分かります。view関数はHttpRequestを引数に受け取り、戻り値としてHttpResponseオブジェクトを返却しています。これはまさにHTTPのやり取りを表現していると言えます。
また、DjangoはHttpResponseオブジェクトを文字列で初期化すると、HTTPレスポンスのボディへ文字列を設定してくれます。

[参考](https://docs.djangoproject.com/en/4.0/ref/request-response/#passing-strings)

### URLconf

viewをつくった後は、期待通りのHTTPレスポンスが得られるかブラウザからリクエストを送って確認したいところです。そのためには、URLとviewを対応づけるURLconfが必要です。プロジェクトディレクトリ・appそれぞれへつくっていきましょう。

#### path関数

各URLconfでは、URLとviewをpathと呼ばれる関数で紐付けます。どのように記述するのか、簡単に書式を見ておきましょう。

[参考](https://docs.djangoproject.com/en/4.0/ref/urls/#path)

> 記法: `path(route, view, kwargs=None, name=None)`

シンプルな使い方では、引数それぞれにURLとviewを設定しておくことで、URLとviewを対応づけることができます。

#### ルート

URLをもとに最初に探索される、いわゆるルートのURLconfを編集します。ここでは、viewとの対応付けをHello World appに任せるため、`include()`を呼び出します。`include()`はappに定義されたurls.pyをimportするような文字列を記述します。

[参考](https://docs.djangoproject.com/en/4.0/ref/urls/#include)

```Python
# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # adminで始まらないURLは、すべてhello_world appのurlsモジュールが受け付ける
    path('', include('hello_world.urls')),
]
```

#### app

続いて、app側でURLconfをつくります。ファイル名はurls.pyとし、書式はプロジェクトディレクトリのものに合わせます。

```Python
# hello_world/urls.py
from django.urls import path

from .views import hello_world

urlpatterns = [
    path('', hello_world)
]
```

これでURLから、先ほどつくったviewをたどれるようになりました。

#### 補足: なぜプロジェクトディレクトリ・appでURLconfを分けるのか

URLと対応するview定義は、一箇所にまとまっていた方が管理しやすいように思えます。なぜわざわざ分ける必要があるのでしょうか。
一言で表現するなら、プロジェクトディレクトリが持つappの知識を最小限にするためです。少し抽象的になったのでもう少し詳しく見てみましょう。
例えば、`/article/`で始まるURLをarticle appで処理すれば、それぞれのpath関数に`/article/`と書く必要が無くなります。こうすることでプロジェクトディレクトリでは、`/article/`以下のURLへのリクエストはarticle appがよしなに処理してくれることを期待できます。
更に、article appでviewを対応づけることで、プロジェクトディレクトリでarticle appのviewをimportするようなことがなくなります。

このように、URLconfを分けておけば、クラスが責務を分割するようにURL管理を分業しながらシンプルに保つことができるのです。

---


## いざ、Hello World

これで準備は整ったので、いよいよHello Worldを試すときがきました。もう一度開発サーバを起動し、`http://127.0.0.1:8000/`へアクセスしてみましょう。

![image](https://user-images.githubusercontent.com/43694794/150127695-70748ab8-c14b-4934-92f0-8d3c5232c1fc.png)

見事に文字列`Hello World`が得られました。念のため生のHTTPレスポンスも覗いておきましょう。

```bash
# HTTPリクエストを送信
$ curl -i localhost:8000

# HTTPレスポンスヘッダ
HTTP/1.1 200 OK
Date: Wed, 19 Jan 2022 12:14:59 GMT
Server: WSGIServer/0.2 CPython/3.9.7
Content-Type: text/html; charset=utf-8
X-Frame-Options: DENY
Content-Length: 11
X-Content-Type-Options: nosniff
Referrer-Policy: same-origin
Cross-Origin-Opener-Policy: same-origin

# ボディ
Hello World
```

色々とヘッダが書かれていますが、最も重要なのはやはり、空行を挟んで書かれたボディです。生のHTTPレスポンスでも期待通り文字列`Hello World`を手に入れられたことが確認できました。


## まとめ

DjangoでHello Worldを試すための流れを追ってきました。シンプルなフレームワークと比べるとずいぶんやることが多いですが、これからのアプリケーション開発にも繋がる大事な基礎なので、しっかり押さえていきましょう。
