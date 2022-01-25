# 概要

Djangoへ入門する始めの一歩として、Hello Worldアプリケーションをつくってみます。

# ゴール

Djangoの基本的な処理に関わるモジュールの役割を知り、文字列Hello Worldを返却するHTTPレスポンスをつくり出すことを目指します。

# 用語整理

* プロジェクト: アプリケーション全体の設定を格納したPythonパッケージ
* アプリケーション(app): 特定の機能を持つWebアプリケーション プロジェクトは、複数のアプリケーションを内包する
* 管理コマンド: `django-admin`や`manage.py`で実行されるコマンド プロジェクトやアプリケーションに関わる操作を担う


## Hello Worldまでの道のり

Hello Worldを題材に、Djangoでアプリケーションをつくるときの大まかな流れを見ていきます。 シンプルなアプリとはいえ、Django特有のものをいくつか扱うことになります。ですので、まずはざっくりと全体像を掴むことから始めます。

### 処理フロー

最初に、これから何をつくるのか箇条書きで俯瞰しておきます。

* アプリケーションの骨組みとなるプロジェクト
* アプリケーションの機能を表現するapp
* HTTPリクエストからHTTPレスポンスを組み立てるview
* URLから対応するviewを呼び出すためのURLconf

それぞれ具体的なイメージをもう少し掘り下げてみましょう。

### プロジェクトとアプリケーション

最初に、`プロジェクト`というアプリケーション全体の設定値などを格納したPythonパッケージをつくります。 続いて、プロジェクトの中にアプリケーションを動作させる上で必要なモジュール群をつくっていきます。Djangoでは、これを`アプリケーション`と呼びます。
ここで、つくる対象のアプリケーションと、Djangoの用語としてのアプリケーションが混ざってしまいそうですね。 後者のアプリケーションは公式でappと記述されているようなので、これからappと表現することにします。

簡単にまとめると、Djangoのアプリケーション開発は、プロジェクトという大枠・少し小さくなったappという骨組みへ、機能を肉付けすることで進めていくことになります。

### viewとURLconf

Hello Worldで求められる機能は、特定のURLへリクエストが送信されたとき、Hello Worldメッセージをレスポンスとして返却することです。これをDjangoでは、view・URLconfと呼ばれるモジュールで実現します。
viewはHTTPリクエストを入力に、HTTPレスポンスを出力する役割を担います。Djangoではクラスや関数で表現されます。
そして、URLconfは、URLと対応するviewをマッピングする役割を担います。DjangoではPythonモジュールで表現されます。

---

DjangoでHello Worldを実現するのに必要な仕組み・モジュールを見ていきました。まだイメージが掴めていなくても、手を動かしていけば徐々に馴染んでくるはずです。一歩ずつ組み上げていきましょう。


## 実装

実際にコマンドを実行したり、コードを書いていきます。これまで見てきたイメージがどのように形づくられるのか、順にたどっていくことにします。

### プロジェクト

早速プロジェクトをつくることから始めましょう。プロジェクトはアプリケーション全体の設定値などを含むPythonパッケージで、`django-admin startproject`コマンドでつくることができます。コマンドの書式は下記の通りです。
[参考](https://docs.djangoproject.com/en/4.0/ref/django-admin/#startproject )

> 記法: `django-admin startproject name [directory]`

nameオプションにはプロジェクト名を、directoryオプションにはプロジェクトディレクトリを指定します。指定方法によって色々と挙動が異なりますが、directoryオプションを毎回指定するようにしておけばシンプルに考えることができます。具体的には、指定されたディレクトリへプロジェクト(nameオプションの値と対応するPythonパッケージ)・manage.py(後述)をつくります。
Hello World以降のアプリケーションもプロジェクトをつくるときは、`django-admin startproject config .`コマンド固定とします。こうすることで、どこに何があるのか明確なルールを定めることができます。


```bash
# プロジェクトをつくる
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

コマンドを実行したディレクトリへ、プロジェクトディレクトリ(config)・manage.pyができあがりました。この機会に全体の概要を押さえておきましょう。

#### __init__.py

ディレクトリがPythonパッケージであることを示すためのモジュールです。

#### asgi.py, wsgi.py

Pythonにおいて、一定のルールでHTTPリクエスト・レスポンスを処理できるようにするためのモジュールです。Webアプリケーションを公開するときまでは意識しなくても大丈夫です。

#### settings.py

アプリケーション全体の設定値を記述したモジュールです。細かな設定値は後々見ていくことにします。

#### urls.py

URLconfと呼ばれる、URLとviewを対応づけるためのモジュールです。

#### manage.py

Webサーバを起動したり、データベースをModelと同期したりと、開発においてよく使う操作をまとめたモジュールです。

---

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
└── views.py
```

プロジェクトと同様、たくさんのファイルができあがりました。それぞれ簡単に見ていきましょう。また、中には機能がイメージしづらいモジュールもありますが、後々触れていく中で理解すれば問題ありませんので、こんなのがあるんだ〜ぐらいのイメージで大丈夫です。

#### __init__.py

ディレクトリがPythonパッケージであることを示すモジュールです。

#### admin.py

管理サイトと呼ばれる機能でModelを扱うためのモジュールです。

#### apps.py

アプリケーションのメタデータを記述するモジュールです。

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

たくさんのモジュールができあがりました。1つ1つを細かく見ていては迷子になってしまうので、ひとまず本筋のWebアプリケーションへ目を向けることにします。
ということで、開発サーバをお試しで動かしてみましょう。方法はフレームワークによってまちまちですが、Djangoはコマンド1つでさくっと動かすことができます。まずは動かした様子を見てみます。

```bash
$ python manage.py runserver
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).

You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.
January 15, 2022 - 14:47:17
Django version 4.0.1, using settings 'config.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

警告が表示されましたが、これはデータベースを扱うようになったとき、解消していきます。 コマンドは、言葉で表現すると`引数にrunserverを指定したmanage.pyをPythonインタプリタで実行した`となります。
[参考](https://docs.djangoproject.com/en/4.0/intro/tutorial01/#the-development-server)

末尾に表示されている通り、`http://127.0.0.1:8000/`へアクセスすることで、開発サーバが動いているか見ることができます。

![image](https://user-images.githubusercontent.com/43694794/149648997-2c226fa1-a7f6-4e1b-b6c9-8d8f943e2de4.png)

無事に動いていることが確認できました。開発サーバはこれから何度も動かすことになるので、起動するまでの流れを押さえておきましょう。
Ctrl+Cで止めることができるので、よきところでHello Worldを試すまでは停止させておきます。

### アプリケーションの登録

開発サーバを試すことができたのでアプリケーションを開発...といきたいところですが、最後にもう1つだけやることがあります。
新しくつくったHello World appをDjangoへ知らせておきます。今は設定しなくても動くには動きますが、Modelを扱うようになると必須となるので、今のうちから習慣づけてしまいましょう。

`config/settings.py`で項目`INSTALLED_APPS`を探します。文字列のリストで表現されているので、末尾へ`hello_world.apps.HelloWorldConfig,`を追記します。こうすることで、Djangoがアプリケーションを探しに行くとき、つくったHello World appを見つけられるようになります。
また、この記述はimport文の形式なので、hello_worldパッケージのappsモジュールのHelloWorldConfigクラスを読み込んでいることを意味しています。

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

---

ようやくアプリケーションをつくる準備が整いました。最初は随分と長い手順に感じるかもしれませんが、経験を重ねていけば、手に馴染んでくるはずです。

### view

まずはHTTPリクエストからHTTPレスポンスを組み立てるviewをつくります。こう書くと難しそうですが、Djangoの枠組みに従うとシンプルに書くことができます。ひとまずできあがったコードを見てみましょう。


```Python
# hello_world/views.py
from django.http import HttpRequest, HttpResponse


def hello_world(request: HttpRequest) -> HttpResponse:
    """
    Hello World文字列をレスポンスとして生成

    :param request: HTTPリクエスト
    :return: Hello World文字列をボディとするHTTPレスポンス
    """
    return HttpResponse('Hello World')
```

関数を眺めていると、最初に書いたviewの役割と対応していることが分かります。view関数はHttpRequestを引数に受け取り、戻り値としてHttpResponseを返却しています。これはまさにHTTPのやり取りを表現していると言えます。
また、DjangoはHttpResponseオブジェクトを文字列で初期化すると、HTTPレスポンスのボディへ文字列を設定してくれます。
[参考](https://docs.djangoproject.com/en/4.0/ref/request-response/#passing-strings)

### URLconf

viewをつくった後は、期待通りのHTTPレスポンスが得られるか確認したいところです。そのためには、URLとviewを対応づけるURLconfが必要です。プロジェクトディレクトリ・appそれぞれへつくっていきましょう。

#### ルート

URLをもとに最初に探索される、いわゆるルートのURLconfを編集します。ここでは、viewとの対応付けをHello World appに任せるため、`include()`を呼び出します。`include()`はINSTALLED_APPSのようにurls.pyをimportするような文字列を記述します。
[参考](https://docs.djangoproject.com/en/4.0/ref/urls/#include)

```Python
# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
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

ここで、URLとviewの対応付けは`path()`により実現されます。第一引数にURL・第二引数をviewを表現する関数「オブジェクト」を設定します。
[参考](https://docs.djangoproject.com/en/4.0/ref/urls/#path)

#### 補足: なぜプロジェクトディレクトリ・appでURLconfを分けるのか

URLと対応するview定義は、一箇所にまとまっていた方が管理しやすいように思えます。なぜわざわざ分ける必要があるのでしょうか。
一言で表現するなら、プロジェクトディレクトリが持つappの知識を最小限にするためです。少し抽象的になったのでもう少し詳しく見てみましょう。
例えば、`/article/`で始まるURLはarticle appで処理することで各処理に`/article/`と書く必要が無くなることでしょうか。こうすればプロジェクトディレクトリでは、`/article/`以下のURLへのリクエストはarticle appがよしなに処理してくれることを期待できます。
更に、article appでviewを対応づけることで、プロジェクトディレクトリでappのviewをimportするようなことがなくなります。

このように、URLconfを分けておけば、クラスが責務を分割するようにURL管理を分業しながらシンプルに保つことができるのです。

---


## いざ、Hello World

これで準備は整ったので、いよいよHello Worldを動かすときがきました。もう一度開発サーバを起動し、`http://127.0.0.1:8000/`へアクセスしてみましょう。

![image](https://user-images.githubusercontent.com/43694794/150127695-70748ab8-c14b-4934-92f0-8d3c5232c1fc.png)

見事文字列`Hello World`が得られました。念のため生のHTTPレスポンスも覗いておきましょう。

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

色々とヘッダが書かれていますが、最も重要なのはやはり、空行を挟んで書かれたボディです。生のHTTPレスポンスでも期待通り文字列`Hello World`を手に入れられたことを確認できました。


## まとめ

DjangoでHello Worldを試すための流れを追ってきました。シンプルなフレームワークと比べるとずいぶんやることが多いですが、これからのアプリケーション開発にも繋がる大事な基礎なので、しっかり押さえていきましょう。
