# 概要

DjangoでつくったHello Worldアプリケーションのテストコードを書いてみます。

## ゴール

Djangoアプリケーションでどのようにテストコードを書くのか、大まかな指針を理解することを目指します。

## 用語整理

* テストフレームワーク
* pytest
* pytest-django

## 全体の方針

Webアプリケーションフレームワークでテストコードを書くには、何を検証するのか・どこまで動作を確かめるのか・具体的なコードでどのように書くのか、といったように考えることがたくさんあります。このまま立ち向かうと何から手をつけてよいか定まらず、行き詰まってしまいます。
ですので、まずはテストコードへ取り掛かる上で何を考える必要があるのか明らかにしておきます。検討すべき対象は、

* どのツール(公式が提供しているもの・それ以外)を選ぶか
* データベースのテーブル・HTTPレスポンス・HTMLのレンダリング結果など、どこまでを検証するか
* テストツール・テスト範囲が決まった後、具体的にどうテストコードを書くのか

といったところでしょうか。この場ですべてを掘り下げるとHello Worldどころの話ではなくなってしまうので、ざっくり全体像を眺める程度にとどめておきます。個々の考え方は少しずつテストコードを書きながら、`なぜそのように書くのか`明記しながら深めていくことにしましょう。

### ツール
れていきますが、基本方針は「なるべくシンプルにテストコードを書けるものが欲しい」としておきます。

### テスト範
詳細は次節で触囲

ここでの範囲は、例えばHTTPレスポンスに含まれるHTML文字列がすべて期待通りであるとするか・あるいは、HTTPレスポンスを組み立てる元となるものが期待通りであるとするか、といったことを指します。つまり、どこまで厳密に検証するか、ということですね。
後々アプリケーションをつくる度に触れていきますが、大方針は「頑張り過ぎないテストコード」を心掛けていきます。すべてを検証しようと思うとメンテナンスしきれない巨大なテストコードが出来上がってしまうので、最低限担保したいゴールを都度定めることを目指します。

### テストの書き方

こちらもテストコードを書くときに詳しく見ていきますが、基本の考え方は「コードもテストコードもシンプルに」を心がけていきます。あまりにも面倒な書き方になってきた・今テストコードで何を検証しているのか一言で表現できない、といった状況になったら実装やテストコードをもう少しシンプルにできないか、考えるようにしていきます。

---

こうして見てみると、色々と考えることが多くて大変そうです。ですが、テストコードを書いていけばDjangoの理解も深まってくるはずなので、一歩ずつ立ち向かっていきましょう。
ということで、以降では最初にどのテストフレームワークを選ぶか検討し、その後Hello Worldアプリケーションのテストコードの書き方をたどっていくことにします。


## テストフレームワークの選び方

Djangoでテストコードを書くとき、真っ先に思い浮かぶのは、[公式](https://docs.djangoproject.com/en/4.0/topics/testing/)で提供されているツールだと思います。
ですが、今回はpytest・pytest-djangoというフレームワーク・ツールを組み合わせてテストコードをつくり上げていきます。

### なぜ公式で用意されているものを使わないのか

実装・テストコードも含め、Django公式から提供されているもので完結させた方がすっきりするように思えます。なぜわざわざ他のツールを導入するのでしょうか。
これは、先ほど名前が挙がったpytestというテストフレームワークがとてもシンプルで使いやすい、ということが大きな理由です。詳細なメリットなどは[公式](https://docs.pytest.org/en/6.2.x/)を見ていただいた方が分かりやすいかと思います。

### pytest-djangoとは

[pytest-django](https://pytest-django.readthedocs.io/en/latest/)にも触れておきます。pytest-djangoはpytestのプラグインの1つで、Djangoアプリケーションのテストコードをpytestで書くとき、さまざまな補助機能を提供してくれます。最も大きなメリットはデータベース操作をよしなにやってくれることですが、実際に踏み込むのはDjangoでデータベースを扱うようになってからにしておきます。
ひとまず今は、pytestとpytest-djangoがあればDjangoのテストコードがシンプルに書ける、ということを頭の隅に置いておきましょう。

#### pytest-djangoのインストール

Djangoと同様、pipでインストールすることができます。

```bash
$ pip install pytest-django
```


## Hello Worldのテスト

ようやく手を動かすところへたどり着きました。Hello Worldという単純な処理ではありますが、アプリケーションを動かすだけでは意識しなかった要素もいくつか触ることになるので、ゆっくりと見ていきましょう。

### ディレクトリ構成

最初にディレクトリ構成を決めておきます。Djangoではappをつくると、`tests.py`を自動生成してくれます。しかし、アプリケーションのコードとテストコードは分かれていた方がシンプルで見やすいです。よって、以降は独立したtestsディレクトリへテストコードを書いていくことにします。より具体的には、アプリケーションのコードはsrc・テストコードはtestsディレクトリと分離させます。
[参考](https://docs.python-guide.org/writing/structure/#test-suite)

### viewのテスト

DjangoのHello Worldではプロジェクト・appを含むさまざまなものがつくられました。ここで、Hello World appにのみ着目してみると、実装したのはview・URLconfだけでした。
新しくつくったview・URLconfが期待通りに動作していれば、Hello World appを検証できたと言えそうです。

#### どう検証するか

view・URLconfが想定した通りに動いてくれるか確かめようと思ったとき、大きな問題に直面します。
アプリケーションを動かしたときは、ブラウザでよしなに何かが表示されたらOK、ぐらいの考えでも問題ありませんでした。しかし、テストコードではどうやって正しさを保証するか、考えなければなりません。これはアプリケーションを実装したときとは別の視点が必要となります。

こう書くと何やら大変そうに思えますが、ありがたいことにDjangoではテストコードのための[Client](https://docs.djangoproject.com/en/4.0/topics/testing/tools/#the-test-client)というモジュールを提供してくれています。
ClientモジュールはHTTPクライアントとして振る舞ってくれるので、`指定したURLへのリクエストから生成されたHTTPレスポンスオブジェクト`を検証していけば、view・URLconfの動作を確かめることができます。もう少し詳しく書くと、`response = client.get('/someURL')`で得られるresponseオブジェクトから、URLconfが対応づけたviewが生成するレスポンスを得ることができます。

### テストコード

どうやって書くかイメージが固まってきたかと思うので、そろそろテストコードを見てましょう。

```Python
# tests/views_test.py
# テスト用のHTTPクライアント
from django.test.client import Client


class TestHelloWorldView:
    """ Hello Worldのviewが呼び出せるか """

    # ステータスコードは正常か
    def test_status_200(self):
        # GIVEN
        client = Client()
        # WHEN
        # URLconfでHello Worldのviewと対応付けたURL(/)へGETリクエストを送信
        actual = client.get('/')
        # THEN
        # HTTPレスポンスのステータスコードを検証
        # ステータスコードが404や500でなければ、URLで対応するviewが存在していると言える
        assert actual.status_code == 200
```

このテストコードで確かめたいことを改めて言葉にすると、`特定のURL(/)へリクエストを送信すると、URLconfをもとに対応するview(hello_world)が呼び出され、HTTPレスポンスが返却されること`となります。完璧とは言えませんが、ある程度担保しておきたい動作を「頑張り過ぎない範囲で」カバーできているのではないかと思います。

#### Client

Clientでgetリクエストを送信するときの書式を見ておきます。
[参考](https://docs.djangoproject.com/en/4.0/topics/testing/tools/#django.test.Client.get)

> 書式: `get(path)`

また、引数のpathはURLのドメイン名以降(ex: `/blog/article`)を指定します。

#### 補足: HTTPレスポンスのボディは検証すべきか

viewの動作を保証するのであれば、HTTPレスポンスのボディまで確かめた方がよさそうです。どうしてステータスコードにとどめているのでしょうか。
これは、ボディにまで踏み込まないことでテストコード・テスト方針をシンプルに保つためです。例えば、複雑なアプリケーションであれば、ボディにはHTMLやスタイル・果てはJavaScriptまで含まれます。これらが混ざった文字列はDjango以外からも影響を受けるので、テストが崩れやすくなってしまいます。

少し話が難しくなってきたのでまとめると、HTTPレスポンスのボディはDjango以外も関わってつくられるので、Djangoの世界に限定してテストコードを書くため、ボディは対象外とします。影響をDjangoに関わるものに閉じてしまえば、安全かつシンプルにテストコードを書くことができます。


### テストを動かす準備

さて、理論の話が続いていたので実践としてテストコードを紹介してきました。しかし、このままではDjangoアプリケーションを検証することができません。テストコードでDjangoを動作させるためには、少しだけDjangoの裏側へ踏み込まなければなりません。具体的には、テストコードへ前処理として、Djangoの前準備を実行させます。
普段アプリケーションを書く上ではあまり意識することのないところですが、この機会に覗いてみましょう。

```Python
# tests/conftest.py
import django
import os
from pathlib import Path
import sys


def pytest_sessionstart(session):
    """ Djangoテストの前処理 """

    # 各種モジュールをimportできるようsrcディレクトリをimportパスへ追加
    src_directory = Path(__file__).resolve().parent.parent / 'src'
    sys.path.append(str(src_directory))

    # 利用する設定ファイル
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    # Djangoの各種モジュールを参照するための準備を整える
    django.setup()
```

上のコードは、pytestでテストを実行するときに前もって実行される処理です。
[参考](https://docs.pytest.org/en/6.2.x/reference.html#pytest.hookspec.pytest_sessionstart)

大きく分けて2つの処理が書かれているので、それぞれもう少し詳しく見てみましょう。

#### sys.path

Pythonはモジュールをimportするとき`sys.path`という、文字列のリストへ記述されたパスを探索します。ここで、普段Djangoアプリケーションを動かすときは、`manage.py`をPythonインタープリタで実行することで、プロジェクトディレクトリが`sys.path`へ追加されます。しかし、テストコードはpytestから実行されるので、何もしなければプロジェクトディレクトリは`sys.path`へ登録されません。
これではテスト対象を見つけられずに困ってしまうので、明示的に`sys.path`へ追加しています。

#### django.setup()

Djangoアプリケーションを書くときは見かけなかった関数が登場しました。`django.setup()`は、Djangoで開発サーバを起動するときに裏側で実行されていた

* INSTALLED_APPSの読み込み
* 設定ファイルの読み込み

を担ってくれます。
[参考](https://docs.djangoproject.com/en/4.0/topics/settings/#calling-django-setup-is-required-for-standalone-django-usage)

また、上で書かれた環境変数定義は、設定ファイルを読み込むときに参照することで、利用すべき設定ファイルを見つけることができます。
つまり、ここで書かれた処理は、Djangoが基準とする設定ファイルの場所を伝え、各種appを読み込むよう依頼しているのです。

---

これらを前処理として実行しておくことで、普段Djangoアプリケーションが開発サーバで動いているような環境でテストコードを動かすことができます。


## まとめ

DjangoのHello Worldを対象にテストコードを書いてきました。アプリケーションをつくるのとはまた違った知識が必要でしたが、実装・テストコード相互に活かせるはずなので、しっかりと身につけていきましょう。