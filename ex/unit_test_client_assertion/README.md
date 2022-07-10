# 概要

`django.test.client.Client`がレスポンスとして返すオブジェクトをつくる仕組みをざっくりとたどってみます。

## ゴール

`django.test.client.Client.get()`などから得られるオブジェクトへテンプレートやコンテキストの情報がどのように設定されるのか、概略を理解することを目指します。

概要を知るだけでは少し物足りないので、ある程度理解できたらDjango + pytestでテストコードを少しだけ書きやすくなるような仕組みがつくれないか考えてみます。より具体的には、`django.test.testcases.SimpleTestCase`のような書き味でテンプレート・コンテキストを検証するテストコードを書けるよう、fixtureを定義してみます。


## 目次

[toc]

## 背景

Django + pytestのような組み合わせでテストコードを書くとき、HTTPリクエスト・HTTPレスポンスに関わる処理は、`django.test.client.Client`に任せることが多いです。例を見ておきましょう。

```Python
from django.test.client import Client


class TestIndex:
    """ トップ画面を表示できるか """

    # viewからレスポンスが得られるか
    def test_status_code(self):
        # テスト用クライアント
        client = Client()
        response = client.get('some_url')
        # 返却されたオブジェクトのステータスコードが正常であることを期待
        assert response.status_code == 200
```

単純に考えれば、Clientから得られたレスポンスである変数`response`の型は、`django.http.HttpResponse`が期待されます。
[公式](https://docs.djangoproject.com/en/4.0/topics/testing/tools/#testing-responses)を見てみると、概ね近いものが得られそうです。正確には、HTTPレスポンスを表現するオブジェクトをよりテストを書きやすくするために拡張したものが手に入ります。

しかし、推論された型は、`Union[{redirect_chain, status_code, url}, WSGIRequest]`のように表示されます。
型情報はHTTPレスポンスとは程遠く、なおかつDjangoがテストコードのために用意してくれたコンテキストやテンプレートの情報もありません。

もう少しイメージを深めるために、テンプレートやコンテキストを検証している処理も見てみましょう。

```Python
from django.test.client import Client


def test_something(self):
    client = Client()
    # 期待するテンプレート名・コンテキストオブジェクトの値
    expected_template_name = 'index.html'
    expected_context_value = 'some message'

    # テスト用クライアントが返却するレスポンス
    response = client.get('some_url')
    # レスポンスからテンプレート名を参照
    template_name = response.templates[0].name
    assert template_name == expected_template_name

    # レスポンスからコンテキストの値を参照
    # コンテキストの辞書そのものを等価比較することはできない
    context_value = response.context.get('some_key', None)
    assert context_value == expected_context_value
```

`django.test.client.Client`から受け取ったレスポンスは、テンプレートがリスト形式であったり、コンテキストがviewで渡した単純な辞書ではなかったりと、各属性が直感的ではない形をしています。
このままでは型も実体も分からないので、十分な理解のもとテストコードが書けなくなってしまいます。

## やりたいこと

公式ドキュメントや曖昧な型情報だけでは、中身を理解してテストコードを書くのが難しそうです。 そこで、`django.test.client.Client`が返却するオブジェクトはどのようにつくられているのか、大まかな流れをたどってみます。
テンプレートやコンテキストがどのように形づくられているか掴めれば、自信をもってHTTPレスポンス周辺のテストコードが書けるようになるはずです。

また、各テストコードで直接リスト形式のテンプレートや、コンテキストオブジェクトを操作するのは冗長に思えます。中身が見えてきたら、これも改善したいところです。
ですので、Djangoが提供している`django.test.testcases.SimpleTestCase`のような書き味でテンプレート・コンテキストを検証できるようなヘルパー関数をつくることにします。

まとめると、Clientのざっくりとした仕組みを知ることで、Django + pytestでHTTPリクエスト・レスポンス周辺のテストコードをシンプルに書けるようになることを目指してみます。


## Clientの実装を追ってみる

さて、ここではDjango本体の実装をいくつか見ていきます。すべてのコードを紹介するとすさまじい文量になってしまうので、ここでは流れを掴める程度につまみ食いしていきます。
言い換えると、今回の目的である「Clientが返却するレスポンスへどのようにテンプレート・コンテキストを設定しているのか」に関わる処理を中心に見ていきます。

※ 以降で見るDjangoのコードは、[バージョン4.0](https://github.com/django/django/tree/4.0)のものを対象としています。

### `django.test.client.Client`

まずはClient周辺の実装から、どのようにレスポンスがつくられているのか見てみます。何はともあれ入り口である`django.test.client.Client`から覗いてみましょう。

```Python
# django/test/client.py
class Client(ClientMixin, RequestFactory):
    """
    A class that can act as a client for testing purposes.
    ... 中略
    """

    # 普段呼び出すClient.get()
    # 通常は、path引数へviewと対応するURLを指定
    def get(self, path, data=None, follow=False, secure=False, **extra):
        """Request a response from the server using GET."""
        self.extra = extra
        response = super().get(path, data=data, secure=secure, **extra)
        # 中略...
        return response
```

つくられたresponseオブジェクトをそのまま返しているようです。

#### メソッド呼び出し順

一見シンプルな処理のように見えますが、内部では色々なメソッドを行ったり来たりしています。迷子にならないよう、要点を押さえながら見るべき処理を定めていきます。
ということで、レスポンスを得るまでにどのようなメソッドが呼ばれるのか、大まかな流れを見てみます。

```Python
# django/test/client.py

# Client.getが始点
class Client(ClientMixin, RequestFactory):
    def get(self, path, data=None, follow=False, secure=False, **extra):
        """Request a response from the server using GET."""
        
        # super()はRequestFactoryを参照
        response = super().get(path, data=data, secure=secure, **extra)
        # 中略...
        return response


class RequestFactory:
    """
    Class that lets you create mock Request objects for use in testing.
    中略...
    """

    # 中略...
    # Client.get() -> RequestFactory.get()
    def get(self, path, data=None, secure=False, **extra):
        """Construct a GET request."""
        data = {} if data is None else data
        return self.generic('GET', path, secure=secure, **{
            'QUERY_STRING': urlencode(data, doseq=True),
            **extra,
        })

    # 中略...
    # RequestFactory.get() -> RequestFactory.generic()
    def generic(self, method, path, data='',
                content_type='application/octet-stream', secure=False,
                **extra):
        """Construct an arbitrary HTTP request."""
        # 中略...
        # 変数rはパスやクエリパラメータなど、リクエストに関わる情報をまとめたもの
        return self.request(**r)


# 再びClientへ戻る
class Client(ClientMixin, RequestFactory):

    # RequestFactory.generic() -> Client.request()
    def request(self, **request):
        """
        The master request method. Compose the environment dictionary and pass
        to the handler, return the result of the handler. Assume defaults for
        the query environment, which can be overridden using the arguments to
        the request.
        """

        # リクエストからレスポンスを組み立てる処理
        # 詳細は後ほど追っていくので、ここでは何やら難しそうな処理からレスポンスがつくられていることが分かればOK
        
        # Curry a data dictionary into an instance of the template renderer
        # callback function.
        data = {}
        on_template_render = partial(store_rendered_templates, data)
        signal_uid = "template-render-%s" % id(request)
        signals.template_rendered.connect(on_template_render, dispatch_uid=signal_uid)
        # Capture exceptions created by the handler.
        exception_uid = "request-exception-%s" % id(request)
        got_request_exception.connect(self.store_exc_info, dispatch_uid=exception_uid)
        try:
            response = self.handler(environ)
        finally:
            signals.template_rendered.disconnect(dispatch_uid=signal_uid)
            got_request_exception.disconnect(dispatch_uid=exception_uid)
        # Save the client and request that stimulated the response.
        response.client = self
        response.request = request
        
        # テンプレート・コンテキストがレスポンスへ設定されている処理!!
        # ここで設定されているテンプレート・コンテキストがどのように組み立てられているか知るのが目標
        
        # Add any rendered template detail to the response.
        response.templates = data.get('templates', [])
        response.context = data.get('context')
        
        # 中略...
        
        return response
```

たくさんのメソッドが呼ばれていますが、ざっくりまとめると、リクエスト情報をよしなに整形した上で、`Client.request()`から呼び出し元へ返すレスポンスを組み立てています。
つまり、`Client.request()`にて、どのようにテンプレート・コンテキストがつくられているのかさえ理解できれば、今回の目的は果たせそうです。


### Client.handler()

テンプレート・コンテキストを見る前に、レスポンスそのものがどのように組み立てられているのか、さらっと見ておきます。


```Python
class Client(ClientMixin, RequestFactory):
    """
    A class that can act as a client for testing purposes.
    中略...
    """
    def request(self, **request):
        """
        The master request method. Compose the environment dictionary and pass
        to the handler, return the result of the handler. Assume defaults for
        the query environment, which can be overridden using the arguments to
        the request.
        """
        # 中略...

        # レスポンスを得る処理
        # イニシャライザより、ClientHandler.__call__()が呼ばれる
        try:
            response = self.handler(environ)
        # 中略...
        
    # イニシャライザ
    # self.handlerはClientHandlerを指す
    def __init__(self, enforce_csrf_checks=False, raise_request_exception=True, **defaults):
        super().__init__(**defaults)
        self.handler = ClientHandler(enforce_csrf_checks)
        self.raise_request_exception = raise_request_exception
        self.exc_info = None
        self.extra = None

class ClientHandler(BaseHandler):
    """
    An HTTP Handler that can be used for testing purposes. Use the WSGI
    interface to compose requests, but return the raw HttpResponse object with
    the originating WSGIRequest attached to its ``wsgi_request`` attribute.
    """
    def __init__(self, enforce_csrf_checks=True, *args, **kwargs):
        self.enforce_csrf_checks = enforce_csrf_checks
        super().__init__(*args, **kwargs)

    # Client.handler()より呼び出される処理
    # djangoがリクエストからレスポンスを組み立てる処理を呼び出す
    def __call__(self, environ):
        # Set up middleware if needed. We couldn't do this earlier, because
        # settings weren't available.
        if self._middleware_chain is None:
            self.load_middleware()

        # django.core.handlers.base.BaseHandler.get_response()を呼び出す
        # Request goes through middleware.
        response = self.get_response(request)
```

※ `BaseHandler.get_response()`はテストコードとは離れてしまうので、出力だけを見ておきます。

テストのために色々と処理は書かれていますが、どうやらレスポンスそのものはDjango本体の処理からつくり出されているようです。
より具体的には、`self.get_response()`から、`<HttpResponse status_code=200, "text/html; charset=utf-8">`のようなHttpResponseオブジェクトがつくられています。

ということで`Client.request()`に目を向けると、ここでつくられるレスポンスは、Djangoが返してくれたHTTPレスポンスオブジェクトへテンプレートやコンテキストの情報を拡張しているようだ、ということが分かります。
つまり、テンプレート・コンテキストが出来上がる仕組みさえ分かれば、Clientの返すレスポンスの実体がそれなりに見えてきそうです。


### `response.templates, response.context`

いよいよ今回の目標であるテンプレート・コンテキストへ立ち向かいます。テンプレートとコンテキストは同時に設定されていることから、一気にまとめて見ていくことにします。
改めて、`Client.request()`を見てみましょう。

```Python
class Client(ClientMixin, RequestFactory):

    # RequestFactory.generic() -> Client.request()
    def request(self, **request):
        
        # Curry a data dictionary into an instance of the template renderer
        # callback function.
        data = {}
        on_template_render = partial(store_rendered_templates, data)
        signal_uid = "template-render-%s" % id(request)
        signals.template_rendered.connect(on_template_render, dispatch_uid=signal_uid)
        
        # 中略...

        # レスポンスのテンプレートとコンテキストを設定している処理
        # data辞書に設定されたものを読みだしている
        # Add any rendered template detail to the response.
        response.templates = data.get('templates', [])
        response.context = data.get('context')
```

こうして見ると、レスポンスのテンプレートとコンテキストは、辞書`data`に設定されたものを見に行っているようです。
ということは、辞書`data`に関わる処理をたどっていけば、テンプレート・コンテキストの中身が理解できそうです。

数行程度の処理でも中身は中々に複雑なので、じっくりと追っていきましょう。

#### partial

```Python
# Curry a data dictionary into an instance of the template renderer
# callback function.
data = {}
on_template_render = partial(store_rendered_templates, data)
```

dataを操作する処理は、`partial()`でpartial objectをつくるところから始まります。

[参考](https://docs.python.org/3/library/functools.html#functools.partial)

つくられたオブジェクトは、`store_rendered_templates()`と呼ばれる関数の第一引数を辞書dataに固定した関数を表現しています。
これを他の関数の引数に渡すことで、`store_rendered_templates()`を呼び出したときに辞書dataを書き換えられるようになります。

少しイメージしづらいですが、一連の処理の流れが掴めれば、このように書く理由も見えてくるはずです。

#### store_rendered_templates

いかにもテンプレートを保存していそうな処理`store_rendered_templates`を見てみます。

```Python
# django.test.client.py
# レンダリングで利用されたテンプレート・コンテキスト情報を保存する
def store_rendered_templates(store, signal, sender, template, context, **kwargs):
    """
    Store templates and contexts that are rendered.

    The context is copied so that it is an accurate representation at the time
    of rendering.
    """
    
    # store引数は、Client.request()で見ていた辞書dataと対応
    # この場でstore引数を書き換えることで、辞書dataもあわせて変更される
    
    # 引数から受け取ったtemplate, contextを辞書dataへ設定
    store.setdefault('templates', []).append(template)
    if 'context' not in store:
        store['context'] = ContextList()
    store['context'].append(copy(context))
```

先ほども見た通り、第一引数は辞書dataに固定されていることから、関数の中で書き換えられた内容も`Client.request()`内部の処理へ反映されます。
つまり、この関数を通じてテンプレートやコンテキストが設定されているようです。
型などを詳しく見ていけば`Client.request()`の返すものも分かってきそうですが、1つ大きな問題があることから、一旦保留にしておきます。

テンプレート・コンテキストの実体を知る上で課題となるのは、`store_rendered_templates()`がいつ・どのように呼び出されるか見えづらいことです。

### signals

テンプレート・コンテキストを設定する処理がいつ呼ばれるか理解するには、Djangoのsignalを知っておかなければなりません。
signalはざっくり表現すると、あるイベント、例えばDjangoがリクエストを処理し始めたとき・Modelを登録したときなどを契機に通知を送るための仕組みです。

[参考](https://docs.djangoproject.com/en/4.0/topics/signals/)

通知内容は、receiverなるコールバック関数によって検知されます。
これだけではイメージしづらいので、`Client.request()`でsignalを扱っている処理を見てみましょう。

```Python
data = {}
on_template_render = partial(store_rendered_templates, data)

signals.template_rendered.connect(on_template_render, dispatch_uid=signal_uid)
```

この処理を通じて、signalがどのようなものか・何をしているのか読み解いていきます。

#### `signals.template_rendered.connect()`

最初に、`signals.template_rendered.connect()`がどのオブジェクトのメソッドを指しているのか、整理しておきます。
これは参照している変数を順にたどれば良く、実体はDjangoが用意しているSignalオブジェクトです。

[参考](https://docs.djangoproject.com/en/4.0/topics/signals/#django.dispatch.Signal)

```Python
# django.test.client.py
# 中略...
# signalsはdjango.test.signalsモジュールを参照
from django.test import signals
```

```Python
# django.test.signals.py
# 中略...
# Djangoが用意しているSignalクラス
from django.dispatch import Signal, receiver

# signals.template_renderedはSignalオブジェクトを指す
# 中略...
template_rendered = Signal()
```

つまり、`signals.template_rendered.connect()`は、`Signal.connect()`と言い換えることができます。

#### `Signal.connect()`

早速概要をドキュメントから見てみましょう。

[参考](https://docs.djangoproject.com/en/4.0/topics/signals/#django.dispatch.Signal.connect)

> 記法: `Signal.connect(receiver, sender=None, weak=True, dispatch_uid=None)`

receiverはコールバック関数で、signalで送られた内容を受け取るためのものです。今回の場合は、テンプレート・コンテキストを辞書dataへ保存します。
`Signal.connect()`でreceiverを登録しておくと、何かしらのタイミングでsignalが通知されたときにテンプレート・コンテキストを保存する`store_rendered_template()`が呼び出されます。

#### `Signal.send()`

signalが通知される何かしらのタイミングとは、`Signal.send()`が呼び出されたときを指します。文字通りsignal(合図)が送られることを意味しています。
コード上では、`template_rendered.send()`が呼ばれると、`store_rendered_template()`が発火します。

もう少しイメージを深めるために、`Signal.send()`の記法も見ておきましょう。

[参考](https://docs.djangoproject.com/en/4.0/topics/signals/#sending-signals)

> 記法: `Signal.send(sender, **kwargs)`

senderは、なんらかのクラスのインスタンスであることが多いです。更に、キーワード引数も渡すことができるようです。
ここで、`store_rendered_templates()`のシグネチャを改めて確認してみます。

```Python
def store_rendered_templates(store, signal, sender, template, context, **kwargs):
```

どうやら、`Signal.send()`のキーワード引数から、テンプレート・コンテキストの情報を受け取っているようです。
つまり、`template_rendered.send()`を呼び出すときに渡しているものを見れば、テンプレート・コンテキストの正体に近づけそうです。


#### `instrumented_test_render()`

`template_rendered.send()`がいつ・どのように呼ばれるのか段階的に見ていきたいところではあります。
しかし、signalはその性質上どこでも通知することができるので、これまでのようにある処理から順を追って見ていてもsignalを送っているところにたどり着くのは困難です。

よって、正攻法とは言いがたいですが、Django本体のソース全体を`template_rendered.send`で検索します。
こうすることで、どこからでも送ることのできるsignalが発火した場所を知ることができます。実際に呼び出しているところを見てみましょう。

```Python
# django.test.utils.py

# Templateのレンダリング処理へ介入するための処理
def instrumented_test_render(self, context):
    """
    An instrumented Template render method, providing a signal that can be
    intercepted by the test Client.
    """
    template_rendered.send(sender=self, template=self, context=context)
    
    # self.nodelist.render()はDjangoがテンプレートを描画する処理の一部
    return self.nodelist.render(context)
```

何やらどこかのクラスのメソッドっぽい処理へ行き着きました。
しかし、これは関数として定義されているので、見ただけでは引数`self`と対応するものは分かりません。

入り口として見ていた`Client.request()`からは離れてしまいましたが、この処理がどのように呼ばれるか紐解いていけばゴールも見えてきそうです。
早速呼び出している処理を見てみましょう。

#### `setup_test_environment()`

`instrumented_test_render()`は、同ファイルの`setup_test_environment()`なる処理が参照しているようです。

[参考](https://docs.djangoproject.com/en/4.0/topics/testing/advanced/#django.test.runner.DiscoverRunner.setup_test_environment)

```Python
# django.test.utils.py
# Djangoでテストコードを実行するときに前処理として呼ばれる処理
def setup_test_environment(debug=None):
    """
    Perform global pre-test setup, such as installing the instrumented template
    renderer and setting the email backend to the locmem email backend.
    """
    
    # 中略...
    
    # Templateクラスの_renderメソッドを上書き
    Template._render = instrumented_test_render
```

中身に入る前に、どのタイミングでこの処理が発火するのか概略を見ておきます。
本来は、Django標準のテストランナー(manage.py testコマンドでテストを実行してくれるもの)から呼ばれます。
ですが、Django + pytestでテストコードを動かすときは、前処理として明示的に呼び出すか、pytest-djangoなどのライブラリを導入する必要があります。

※ pytest-djangoでは当該処理を前処理として呼び出すfixtureが定義されています。

---

`setup_test_environment()`がテストの前処理の役割を持つことが理解できたところで、`instrumented_test_runner()`を参照している処理を見てみます。

```Python
Template._render = instrumented_test_render
```

Djangoのテンプレートを表現するTemplateクラスの`_render()`属性を上書きしています。
このように書いた理由は、Djangoがテンプレートをレンダリングしている処理にテストで介入するためです。

テストコードにおいて、Djangoがテンプレートを描画する処理は次のように動作します。

* 描画時点のテンプレート・コンテキスト情報をもとにsignal template_renderedを送信
* Djangoがテンプレートをレンダリング

テンプレートをレンダリングする度に、その時点でのテンプレート・コンテキストの情報を保存しておけば、とてもテストがしやすくなります。
HTTPレスポンスに含まれるHTMLなどの結果ではなく、過程のテンプレートやコンテキストをもとに期待値を定義できるのです。

### Template

いかにもな名前のTemplateクラスを追っていきます。おそらく、このクラス自身にはテンプレートの情報が、そして、このクラスに定義されたレンダリング処理にはコンテキストの情報が書かれるはずです。
それが分かればついにゴールへたどり着けそうです。とはいえテストコードとはどんどん離れてきたので、要点をつまむ程度に見ていくことにします。

まずはクラスの概要をざっと見てみます。

```Python
# django.template.base.Template

class Template:
    def __init__(self, template_string, origin=None, name=None, engine=None):
        # 中略
        # テンプレートそのものの情報を設定
        # name属性は多くの場合、テンプレートのファイル名が指定される
        self.name = name
        self.origin = origin
        self.engine = engine
        self.source = str(template_string)  # May be lazy.
        self.nodelist = self.compile_nodelist()
        
    # 上書きされた処理
    # 処理を呼び出す前に自身の情報と引数のコンテキストと共にsignalを送信
    def _render(self, context):
        return self.nodelist.render(context)

    # _renderの呼び出し元
    def render(self, context):
        "Display stage -- can be called many times"
        with context.render_context.push_state(self):
            if context.template is None:
                with context.bind_template(self):
                    context.template_name = self.name
                    return self._render(context)
            else:
                return self._render(context)
```

ここでのname属性は、テストコードを書くときに期待値としている、レンダリングされたテンプレート名(例: index.html)を表現しています。
そして、`Template.render()`さえ押さえてしまえば、コンテキストの中身も掴めそうです。

#### Template.renderはどのように呼ばれるか

`Template.render()`を呼び出している処理を追っていきます。あまり深くまで入り込むと戻ってこられなくなりそうなので、表面的な部分から重要なところを抜き出してみます。
例として、テンプレートのレンダリング結果をHTTPレスポンスとして設定しているviewの処理を見てみます。

```Python
def fortune_telling(request: HttpRequest) -> HttpResponse:
    """
    おみくじ結果画面表示

    :param request: HTTPリクエスト
    :return: おみくじ結果画面をボディに持つHTTPレスポンス
    """
    fortune = fortune_module.tell_fortune()
    context = {
        'fortune': fortune
    }

    # render_to_string()でテンプレートを文字列へ
    return HttpResponse(render_to_string('fortune.html', context=context))
```

コンテキストをもとにテンプレートをレンダリングする処理`render_to_string()`へ指定したテンプレートはどのように渡されるのでしょうか。
少しだけ潜ってみましょう。

```Python
# django.template.loader.py
def render_to_string(template_name, context=None, request=None, using=None):
    """
    Load a template and render it with a context. Return a string.

    template_name may be a string or a list of strings.
    """
    
    # 得られたTemplateオブジェクトのrenderメソッドを呼び出す
    if isinstance(template_name, (list, tuple)):
        template = select_template(template_name, using=using)
    else:
        template = get_template(template_name, using=using)
    return template.render(context, request)
```

それっぽい処理が呼ばれています。
ここでのテンプレートオブジェクトを得る処理はかなり複雑なので、ブレイクポイントをもとにした呼び出し順を見るにとどめておきます。

![image](https://user-images.githubusercontent.com/43694794/178094125-4307a1fb-81da-4d95-a4db-87dc1702ade0.png)

確かに、`render_to_string()`から`Template.render()`が呼ばれていることが確認できました。
ここから、「viewで渡したコンテキストをそのまま受け取っている」ことが分かります。

#### `instrumented_test_render`が引数として受け取るもの

`Template._render()`の概要が見えてきたので、signalを送っている`instrumented_test_render()`へ戻ります。
あちこちを行ったり来たりしていたので、改めてコードを確認しておきます。

```Python
# django.test.utils.py

# Templateのレンダリング処理へ介入するための処理
def instrumented_test_render(self, context):
    """
    An instrumented Template render method, providing a signal that can be
    intercepted by the test Client.
    """
    template_rendered.send(sender=self, template=self, context=context)

    # self.nodelist.render()はDjangoがテンプレートを描画する処理の一部
    return self.nodelist.render(context)
```

`Template._render()`を見て分かったことをまとめてみます。

* ここでのselfはTemplateオブジェクト より具体的には、viewのレンダリングで参照されるテンプレートを表現したものを指す
* contextはviewのレンダリングで渡されたものとほぼ等価と見てよい

まとめると、`template_rendered.send()`でシグナルと共に送られるテンプレート・コンテキストの情報は、viewのレンダリングで参照していたものを表していたことが分かりました。


### 復習-処理の流れ

少し駆け足気味でしたが、`Client.request()`が受け取っていたテンプレート・コンテキストがどこからつくられたのか、概要をたどることができました。
たくさんの処理を見てきたので、迷子にならないよう、改めて処理の流れを復習しておきましょう。その後で本当のゴール、すなわち`Client.request()`が返しているものを読み解いていきます。

---

要点を押さえるためにも、各処理がどのように連携しているのか、箇条書きでまとめてみます。

* テストコードでviewを検証するために`Client.get()`から処理を開始
* リクエスト情報をもとに`Client.request()`が呼ばれる
* テンプレートを描画する度に、描画時点のテンプレート・コンテキスト情報を保存しておけるようにsignalを登録 登録対象は、`Template._render()`
* DjangoのHTTPレスポンス生成処理を実行

* パス情報をもとに呼び出すべきviewを探索
* viewからHTTPレスポンスを組み立て
* `render_to_string()`のような、テンプレートから文字列を組み立てる処理をコンテキストをもとに呼び出し
* `Template.render()`(テンプレートのレンダリング処理)を実行
* `Template._render()`にsignalを送る処理が登録されていることから、描画処理の前に、`render_to_string()`へ渡されたコンテキストや、対応するテンプレート情報と共に`template_rendered signal`を送信

* signalのreceiver `store_rendered_templates()`で辞書dataへテンプレート・コンテキスト情報を保存
* `Client.request()`が返却するレスポンスオブジェクトへテンプレート・コンテキスト情報を設定

一言でまとめると、`Client.request()`で定義した処理のおかげで、各viewがテンプレートをレンダリングしたときのテンプレート・コンテキスト情報が参照できるようになります。
これは、viewで参照されたテンプレート・コンテキストが期待通りか検証したい、というviewのテストコードの目的にもぴったりはまります。

---

### `store_rendered_templates()`

ようやく、`store_rendered_templates()`へどのようなものが保存されているのか知ることができました。
具体的なコードと理解を照らし合わせるためにも、もう一度該当の処理を見てみます。

```Python
# django.test.client.py
def store_rendered_templates(store, signal, sender, template, context, **kwargs):
    """
    Store templates and contexts that are rendered.

    The context is copied so that it is an accurate representation at the time
    of rendering.
    """

    # store引数は、Client.request()で見ていた辞書dataと対応
    # この場でstore引数を書き換えることで、辞書dataもあわせて変更される

    # viewでは複数のテンプレートを組み合わせてレスポンスをつくることもあるので、
    # レンダリングの度に描画したテンプレート情報を保存
    store.setdefault('templates', []).append(template)
    
    # コンテキストもテンプレートと同様
    if 'context' not in store:
        store['context'] = ContextList()
    store['context'].append(copy(context))
```

呼び出し方が分かることで、この関数に書かれた処理が「なぜそのように書くのか」見えてきました。理解を忘れないよう具体的な言葉にしておきましょう。
`store_rendered_templates()`はテンプレートがレンダリングされる度に、レンダリング時のテンプレート・コンテキスト情報を保存する処理です。

ということは、各レンダリング処理のテンプレート・コンテキストを保存しておかなければなりません。
よって、テンプレートとコンテキストはリスト形式で保存されるのです。

---

これで、`Client.get()`から得られたレスポンスからテンプレート情報を取り出すときに、`response.templates`のように書かないといけない理由を突き止めることができました。

ただ、コンテキストは単純なリストではないようなので、もう少し掘り下げてみましょう。


### Context

Django + pytestで`Client.get()`から得られたレスポンスのコンテキストオブジェクトを検証しようと思ったとき、次のように書いたことがあるかもしれません。

```Python
# コンテキストの運勢要素は関数から生成されたか
def test_context_value(self):
    client = Client()
    context = {'some_key': 'some_value'}
    
    # レスポンスを生成
    # コンテキストがviewで渡したものと等しいか比較
    response = client.get('some_url')
    assert response.context == context
```

contextという属性名から、なんとなくviewのレンダリング処理に渡したコンテキストと同じものが得られることを期待しています。
しかし、このテストは通らず、実際にレスポンスに設定されていたコンテキストは以下のように表示されます。

```bash
Expected :{'some_key': 'some_value'}
Actual   :[{'True': True, 'False': False, 'None': None}, {'some_key': 'some_value'}]
```

これは、レンダリング処理に渡した辞書ではなく、`django.template.context.Context`オブジェクトを表しています。
表示されているリストは、Contextオブジェクトのdicts属性を`__repr__()`で出力したものです。

※ 先頭の辞書は`django.template.context.BaseContext`でbuiltinsとして定義されているものです。詳しい説明はありませんでしたが、おそらくDjangoがテンプレートを解釈するときに参照していると思われます。

なにやら難しそうに見えますが、Contextオブジェクトは辞書アクセス用のメソッドをいくつか用意しているので、テンプレートのレンダリング処理で参照される読み取り専用の辞書ぐらいに思っておいて大丈夫です。
テストコードでは、`Context.get()`からコンテキストのキーでアクセスすることで、値を取り出すことできます。

---

`Client.get()`から得られたレスポンスのコンテキストがこのような形になっているということは、`store_rendered_templates()`で設定されていたものも、Contextオブジェクトであったことが分かります。
続いて、各レンダリングで参照したContextオブジェクトをリストっぽく保存しているものを見てみましょう。

### ContextList

`store_rendered_templates()`では、レンダリングで参照したコンテキストを`django.test.utils.ContextList`というオブジェクトへ追加しています。

```Python
# store_rendered_templatesのコンテキストを設定している処理

if 'context' not in store:
    store['context'] = ContextList()
store['context'].append(copy(context))
```

ContextListはlistを継承したオブジェクトで、複数あるコンテキストを1つの辞書として扱えるようにするためのインタフェースを提供します。小難しい表現となってしまいましたが、実装を見てみれば、どのようにContextオブジェクトを扱っているのか掴めてくると思います。

```Python
# django.test.utils.py
class ContextList(list):
    """
    A wrapper that provides direct key access to context items contained
    in a list of context objects.
    """
    def __getitem__(self, key):
        if isinstance(key, str):
            for subcontext in self:
                if key in subcontext:
                    return subcontext[key]
            raise KeyError(key)
        else:
            return super().__getitem__(key)

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default
    
    # 中略...
```

例えば、テストコードではリスト形式のContextListオブジェクトへ`context['some_key']`または`context.get('some_key')`のようにアクセスすると、各レンダリングで参照したコンテキストをすべて探しに行ってくれます。

---

### たどり着いたゴール

これでコンテキストの中身も知ることができました。
つまり、今回の大きな目標である、`Client.get()`から得られるレスポンスへどのようにテンプレートやコンテキストが設定されているのか知ることができました。

今なら、最初にテンプレートやコンテキストを扱うテストコードを書いたときに抱いていた疑問も解消できるはずです。
テストコードを再度見ながら、確認してみましょう。

```Python
from django.test.client import Client


def test_something(self):
    client = Client()
    # 期待するテンプレート名・コンテキストオブジェクトの値
    expected_template_name = 'index.html'
    expected_context_value = 'some message'

    # テスト用クライアントが返却するレスポンス
    response = client.get('some_url')
    # レスポンスからテンプレート名を参照
    template_name = response.templates[0].name
    assert template_name == expected_template_name

    # レスポンスからコンテキストの値を参照
    # コンテキストの辞書そのものを等価比較することはできない
    context_value = response.context.get('some_key', None)
    assert context_value == expected_context_value
```

#### なぜテンプレートはリスト形式なのか

テンプレートはレンダリングの度にsignalを通じて保存されるので、リスト形式のものがレスポンスへ設定されます。

#### なぜコンテキストは辞書のはずなのにviewで渡したものと異なるのか

コンテキストもレンダリングの度に保存されることから、複数のものが存在し得ます。
しかし、リスト形式の辞書ではテストコードで扱いづらいことから、listのインタフェースを持つContextListオブジェクトがレスポンスへ設定されます。
よって、viewで渡したコンテキストの辞書とは異なるものになります。

---


## Clientから得られるレスポンスをpytestでも検証したい

全体の流れをたどり、`Client.get()`の返すものを理解することができました。
ここで終わっても今回の目的は果たせていますが、時間が経つとレスポンスに設定されたテンプレート・コンテキストの情報がどのようなものだったか忘れてしまいそうです。

そこで、テンプレート・コンテキストを表現する型を定義し、テストコードでシンプルに扱えるようにするfixtureをつくることで、知識を再利用できる形で残しておきます。
これだけだとイメージしづらいので、実際につくったfixtureと、テストコードの利用例を見てみましょう。

```Python
# conftest.py
from typing import Union

from django.http import HttpResponse
from django.template.base import Template
from django.test.utils import ContextList
from django.template.context import Context


class ClientResponseAttribute:
    """ TestClientがresponseオブジェクトへ注入する追加の属性を表現することを責務に持つ """
    templates: list[Template]
    context: Union[Context, ContextList]


# Client.get()から得られたレスポンスをテストコードで参照するときの型 テストで利用する型のみに簡略化
# ※ 本来得られるレスポンスは双方の性質を持つ交差型である
# しかし、2022年7月時点では交差型が無いこと・型の恩恵を得る手段がUnionしかないことからUnion型で定義した
TypeClientResponse = Union[HttpResponse, ClientResponseAttribute]


class AssertionHelper:
    """ django.test.TestCaseが担っていたassertionを表現することを責務に持つ """

    def assert_template_used(self, response: ClientResponseAttribute, template_name: str):
        """
        TestClientがレスポンスを生成したとき、指定のテンプレートファイルが利用されたことを表明

        :param response: TestClientが返却するレスポンスオブジェクト
        :param template_name: テンプレートファイル名
        """

        template_names = [template.name for template in response.templates if template.name is not None]
        assert template_name in template_names

    def assert_context_get(self, response: ClientResponseAttribute, key: str, value):
        """
        コンテキストオブジェクトのキーで対応する要素が期待通りであることを表明

        :param response: TestClientが返却するレスポンスオブジェクト
        :param key: コンテキストの対象キー
        :param value: 期待値
        """
        context = response.context
        assert context.get(key) == value
```

```Python
class TestFortuneTelling:
    """ おみくじ画面のテスト """

    # おみくじ画面のテンプレートを参照しているか
    def test_use_result_template(self, assertion_helper):
        client = Client()
        expected = 'fortune.html'
        
        response = client.get('おみくじのURL')
        
        # レスポンスから得られるテンプレートを検証
        assertion_helper.assert_template_used(response, expected)

    # コンテキストの運勢要素は関数から生成されたか
    def test_context_fortune(self, assertion_helper):
        client = Client()
        context_key_of_fortune = 'fortune'
        expected = '大吉'
        
        response = client.get('おみくじのURL')
        
        # レスポンスから得られるコンテキストを検証
        assertion_helper.assert_context_get(response, context_key_of_fortune, expected)
```

`Client.get()`が返すレスポンスに設定されたテンプレート・コンテキストの情報を、型によってコード上に知識として記すことができました。
簡易的なものではありますが、これでDjango + pytestでテンプレートとコンテキストを検証するテストコードを以前よりも中身を理解して書けるようになるはずです。


#### 補足: なぜresponseの型はWSGIRequestを含むものに推論されたのか

最後に補足として、`Client.get()`が返すオブジェクトの型推論が崩れていた理由を見ておきます。
そもそもここで正しく型が記述されていれば、ここまで苦労することもなかったはずです。

とはいえ、Django本体には型ヒントが書かれていないかつ、複雑なフローで処理が呼び出されていることから、正確に推論するのは困難です。
ひとまず推論された結果がなぜそのようになったのか、概略だけ見ておきましょう。

型情報は、`Union[{redirect_chain, status_code, url}, WSGIRequest]`のように書かれておりました。
まず、WSGIRequestは、RequestFactoryから`self.request()`で呼ばれた`Client.request()`ではなく、`RequestFactory.request()`をもとに型が推論されたことによります。
そして、辞書っぽいオブジェクトの型は、`Client.get()`でリダイレクトを扱う処理から推論されました。

```Python
# django/test/client.py

def get(self, path, data=None, follow=False, secure=False, **extra):
    """Request a response from the server using GET."""
    self.extra = extra
    response = super().get(path, data=data, secure=secure, **extra)

    # リダイレクト用の処理により、{redirect_chain, status_code, url}の型が推論された
    if follow:
        response = self._handle_redirects(response, data=data, **extra)
    return response
```



## まとめ

`Client.get()`が返すレスポンスに設定されたテンプレート・コンテキストオブジェクトがどのようなものであるか、概要を追ってきました。
大変な道のりではありましたが、Djangoがテストコードのために用意してくれたモジュールが何をもたらしてくれるのか、少しでも見えてきたら幸いです。
