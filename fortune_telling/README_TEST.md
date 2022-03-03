# 概要

Djangoでつくったおみくじアプリケーションのテストコードを書いていきます。

## ゴール

逆引きや、viewでつくりだされるコンテキストオブジェクトをどのように検証するのか、理解することを目指します。


## 復習-テストツール・テスト範囲

慣れるまでは、Djangoのテストコードの大枠を復習するところから始めていきましょう。
まずは、テスト方法を確認しておきます。テスティングフレームワークであるpytestと、pytest用のプラグインであるpytest-djangoを組み合わせながら書いていきます。また、デフォルトでappに`tests.py`が用意されていますが、アプリケーションとテストコードを独立させるため、srcディレクトリと同階層にtestsディレクトリをつくることにします。

そして、テスト範囲は、viewがつくり出すレスポンスオブジェクトの一部をテスト用クライアントで確認するに留めます。これにより、テストコードが複雑になり過ぎることを防げます。

### ディレクトリ構成

具体的なディレクトリ構成も見ておきます。Hello Worldのテストコードを参考に、以下のようなファイル・ディレクトリをつくっておきます。

```bash
$ tree
├── src
# 中身は省略...
└── tests
    ├── __init__.py
    ├── conftest.py
```

conftest.pyを再掲しておきます。conftest.pyがあることで、テストコードでDjangoを動かし、かつsrcディレクトリ配下のモジュールを実装コードと同じようにimportできるようになります。

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

---

## トップ画面

準備が整ったので、つくった機能を検証していきます。まずはトップ画面から始めていきましょう。
実装をHello Worldと比較すると、返却するHTTPレスポンスが単純な文字列からHTMLファイルをもとにしたものへ変わりました。HTMLファイルの中身まで入り込むとテストコードがメンテナンスしきれなくなるので、

* ステータスコード
* レンダリングで参照されたテンプレートファイル名

を見るに留めておきます。トップ画面へのリクエストからステータスコード200(正常)が得られ、テンプレートファイルとして`index.html`ファイルを参照していたことが分かれば、テンプレートをもとに期待通りのレスポンスが得られると考えて良さそうです。
早速確かめてみましょう。

### ステータスコード

最初に、ステータスコードを確認しておきます。ステータスコードはHello Worldでも検証したので、復習となります。

#### 名前付きURL

ただ、一点だけ異なるところがあります。それは、URLの指定方法です。
トップ画面からおみくじを引くとき、リンクへ記述するURLのところへ、`名前付きURL`を指定していました。これは、URLのべた書きを防ぐことでメンテナンス性を高めるためです。
ということは、テストコードでもURLはべた書きせずに済ませたいところです。そこで、テストクライアントからリクエストを送信するとき、URLを逆引きで得られるようにします。

細かいところは後ほど見ることにして、ひとまずテストコードを先に眺めておきましょう。

```Python
# tests/views_test.py
from django.test.client import Client
# 逆引きのための関数
from django.urls import reverse


class TestIndex:
    """ トップ画面を表示できるか """

    # viewからレスポンスが得られるか
    def test_status_code(self):
        # GIVEN
        client = Client()
        named_url = 'おみくじ:トップ'
        # WHEN
        actual = client.get(reverse(named_url))
        # THEN
        assert actual.status_code == 200

```

重要なのは、`client.get()`の引数です。逆引きでURLを得るために`reverse()`を呼び出しています。書式から見てみましょう。
[参考](https://docs.djangoproject.com/en/4.0/ref/urlresolvers/#reverse)

> 書式: `reverse(viewname, urlconf=None, args=None, kwargs=None, current_app=None)`

見るべきは第一引数のみで、`viewname`へ名前付きURLを指定します。view関数を直接記述することもできますが、確かめたいのは名前付きURLと実際のURLの結びつきなので、名前付きURLを書くことにします。
また、名前付きURLは、`app名:path関数のname引数で設定したview名`の形式で記述します。

逆引きの方法が分かれば、あとはHello Worldと同じ流れでテストコードを見ることができます。実際に動かして、テストが通ることも見ておきましょう。

```bash
# 出力を抜粋
============================= test session starts ==============================
collecting ... collected 1 item

views_test.py::TestIndex::test_status_code PASSED                        [100%]
```

### 参照したテンプレート

続けて、view関数が参照したテンプレートの情報を検証していきます。より具体的には、レスポンスをつくるときに読み込まれたHTMLファイルのファイル名が期待通りのものであるか、確かめます。
基本的な流れは先ほどのテストコードとほとんど同じなので、まずは雰囲気を見ておきます。

```Python
# 抜粋
# tests/views_test.py
class TestIndex:
    """ トップ画面を表示できるか """
    # 中略...
    # トップ画面のテンプレートを参照しているか
    def test_use_index_template(self):
        # GIVEN
        client = Client()
        named_url = 'おみくじ:トップ'
        expected = 'index.html'
        # WHEN
        response = client.get(reverse(named_url))
        # templates属性の先頭要素のname属性にテンプレートファイル名が格納されている
        actual = response.templates[0].name
        # THEN
        assert actual == expected
```

注目すべきは、レスポンスオブジェクトの`templates`属性へアクセスしていることです。ここには、テンプレートを表現するTemplateオブジェクトのリストが設定されています。今回は1つのHTMLファイルしか見ていないので、先頭の要素へアクセスします。
そして、Templateオブジェクトのname属性には、欲しかった、view関数が参照したHTMLファイルのファイル名が書かれています。
[参考](https://docs.djangoproject.com/en/4.0/topics/testing/tools/#django.test.Response.templates)

このテストコードにより、トップ画面へのリクエストに対するレスポンスは、トップ画面のテンプレートと対応する`index.html`ファイルをもとにつくられていたことを保証できます。

```bash
============================= test session starts ==============================
collecting ... collected 1 item

views_test.py::TestIndex::test_use_index_template PASSED                 [100%]
```

---

## おみくじ結果画面

さて、トップ画面は問題なくテストすることができました。続いて、コンテキストを扱うおみくじ結果画面を見ていきましょう。

### おみくじ

Djangoとは少し逸れますが、コンテキストオブジェクトのもとになる、おみくじを引くための関数にも少し触れておきます。
おみくじによる運勢はあらかじめ決まっているものではなく、毎回ランダムに算出されます。これまでのように期待値を固定の値(200, index.htmlなど)にすると、運勢によってテストが通ったり通らなかったりしてしまいます。

それではテストとして何も保証できないので、ここでは期待値の範囲を広げることにします。具体的には、ランダムに導き出された運勢がなんであれ、運勢の候補に含まれていれば、よしとします。
ランダムなものを扱うテストは、対象の処理がどこまで影響するかによって方針が変わってきますが、今回はちょっとした運勢なので、このぐらいで妥協しておきます。

```Python
# tests/fortune_telling_test.py
from fortune_telling.fortune import tell_fortune, FORTUNE_CANDIDATE


# 運勢は候補の中から選ばれるか
def test_fortune_in_candidate():
    # GIVEN
    sut = tell_fortune
    # WHEN
    actual = sut()
    # THEN
    assert actual in FORTUNE_CANDIDATE
```

テストコードでも、ランダムな運勢が候補の中のいずれかであることを期待している旨が書かれています。

```bash
============================= test session starts ==============================
collecting ... collected 1 item

fortune_telling_test.py::test_fortune_in_candidate PASSED                [100%]
```

繰り返しテストを実行しても、問題なく通るようになっているはずです。


### view(コンテキスト)

さて、Djangoへ戻ることにしましょう。おみくじの結果を導き出す処理は、コンテキストオブジェクトを軸に検証していきます。コンテキストオブジェクトは、先ほどまで見てきたおみくじ関数をもとにつくりだされます。
ステータスコード・参照したテンプレートのテストコードはトップ画面とほとんど変わらないので、割愛します。詳しくは[テストコードへのリンク](https://github.com/a-pompom/Django-playground/blob/main/fortune_telling/tests/views_test.py)を確認してみてください。

---

おみくじアプリにおいて、コンテキストオブジェクトはランダム要素の関わる関数からつくり出されます。再度コンテキストが関わる処理を見ておきましょう。

```Python
# src/fortune_telling/views.py
# コンテキストオブジェクト抜粋
# おみくじ関数の戻り値(運勢)をコンテキストオブジェクトへ設定
fortune = fortune_module.tell_fortune()
context = {
'fortune': fortune
}
```

先に触れておくと、コンテキストもテンプレートと同じように、レスポンスオブジェクトの属性から取り出すことができます。つまり、テンプレートと似たような記述から、コンテキストオブジェクトも期待値と比較することができます。テストコードのイメージでも見ておきましょう。
[参考](https://docs.djangoproject.com/en/4.0/topics/testing/tools/#django.test.Response.context)

```Python
# tests/views_test.py
# 中略...
class TestFortuneTelling:
    # 中略...
    
    def test_context_fortune(self):
        # GIVEN
        client = Client()
        named_url = 'おみくじ:結果'
        # コンテキストオブジェクト(辞書)のおみくじの結果と対応するキー
        context_key_of_fortune = 'fortune'
        # 期待結果 ※ このままでは問題あり
        expected = '大吉'

        # WHEN
        response = client.get(reverse(named_url))
        # response.contextは辞書のコンテキストオブジェクトが得られるので、辞書として操作
        actual = response.context.get(context_key_of_fortune, None)
        # THEN
        assert actual == expected
```

これで、テンプレートとあわせて参照されるコンテキストオブジェクトを確かめる方法も理解することができました。
しかし、運勢はランダムに導き出されるものであることから、このままではテストが通らないことがあります。これでは問題なので、常に同じ結果を得る手段がないか考えてみましょう。

#### モック化

問題なのは、テストクライアントを介して処理されるview関数から、ランダム要素の関わる関数が呼ばれていることです。ランダムというとおみくじアプリ特有の問題に見えますが、WebAPI呼び出しやメール送信など、Webアプリケーションでは馴染み深い処理もこの問題に共通しています。
つまり、処理の結果をアプリケーションで制御できないもの(ランダムなもの・外部API側のエラーなど)をそのまま扱うと、テストコードの動作が非常に不安定になります。

テストフレームワークでは、このような問題を解決するため、`モック化`という仕組みが提供されています。
`mock`という単語がレプリカをつくるといった意味を持つように、モック化は、アプリケーションで制御できない処理をテストコード用のレプリカに置き換えるといったことを指しています。
おみくじの例では、ランダムな運勢を出力する関数を、固定の文字列を返却する関数(レプリカ)で代用することがモック化に相当します。

まとめると、モック化を導入することで、自身の開発しているアプリケーションに閉じた世界でテストができるようになります。

[参考](https://stackoverflow.com/questions/2665812/what-is-mocking)

#### monkeypatch

本題に戻って、ランダム要素の関わるおみくじ関数をモック化してみましょう。pytestでは、モック化のための仕組みとして、`monkeypatch`というfixtureが提供されています。
monkeypatch fixtureでモック化することで、特定のモジュールに属する関数の戻り値を固定させることができます。おみくじアプリの例で言い換えれば、おみくじ関数の戻り値を「大吉」といった特定の運勢で固定できるようになります。
[参考](https://docs.pytest.org/en/6.2.x/monkeypatch.html#simple-example-monkeypatching-functions)

では、具体的にどのようにモック化するのか、テストコードから見てみましょう。


```Python
# tests/views_test.py
from pytest import MonkeyPatch
# 中略...
class TestFortuneTelling:
    # 中略...

    # コンテキストの運勢要素は関数から生成されたか
    # fixtureはテスト関数の引数で受け取る
    def test_context_fortune(self, monkeypatch: MonkeyPatch):
        # GIVEN
        client = Client()
        named_url = 'おみくじ:結果'
        context_key_of_fortune = 'fortune'
        expected = '大吉'
        
        # fortuneモジュールのtell_fortune属性を、「文字列 '大吉'」を返却する関数でモック化
        monkeypatch.setattr(fortune, 'tell_fortune', lambda: expected)

        # WHEN
        response = client.get(reverse(named_url))
        actual = response.context.get(context_key_of_fortune, None)
        # THEN
        assert actual == expected
```

関数をモック化しておくことで、安定してテストコードが動作するようになってくれました。

```bash
============================= test session starts ==============================
collecting ... collected 1 item

views_test.py::TestFortuneTelling::test_context_fortune PASSED           [100%]

============================== 1 passed in 0.08s ===============================
```


#### 補足: なぜモック化対象の関数を`モジュール名.関数名`の形式で呼び出しているのか

さて、おみくじ関数を呼び出すとき、`モジュール名.関数名`と記述していたかと思います。こんな冗長な書き方をしなくとも、モジュールから関数をimportし、関数名だけで呼び出した方がシンプルです。
なぜこのような書き方をしているのでしょうか。

これは、monkeypatchがモック化するときに内部で利用している、組込関数`setattr()`の挙動によるものです。
挙動について詳しく言及しているドキュメントは見当たりませんでしたが、簡単な実験コードから、関数名だけの記述では問題となることを見ることができます。

```Python
# fortune.py

def tell_fortune():
  return 0
```

```Python
# main.py
import fortune
from fortune import tell_fortune

# 0
print(tell_fortune())
# 0
print(fortune.tell_fortune())
# True
print(fortune.tell_fortune == tell_fortune)

setattr(fortune, 'tell_fortune', lambda: 999)

# 0
print(tell_fortune())
# 999
print(fortune.tell_fortune())
# False
print(fortune.tell_fortune == tell_fortune)
```

このような動作をすることから、モック化したい処理はモジュール名まで記述した上で呼び出した方がよい、ということを覚えておきましょう。

※ おみくじアプリの例では、viewsモジュールのtell_fortune属性をモック化することで呼び出し元を関数名とすることができますが、何をモック化しているのかが見えづらくなるので避けた方が無難です。

## まとめ

Djangoのおみくじアプリでテストコードを書いてきました。テストコードから、テンプレートやコンテキストが期待通りのものか検証する方法を見てきました。
いずれも、テストクライアントの提供するレスポンスオブジェクトから、シンプルに確かめることができます。