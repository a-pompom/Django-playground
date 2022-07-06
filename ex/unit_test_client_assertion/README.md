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
    context_value = response.context.get('some_key', None)
    assert context_value == expected_context_value
```

`django.test.client.Client`から受け取ったレスポンスは、テンプレートがリスト形式であったり、コンテキストが単純な辞書ではなかったりと、各属性が直感的ではない形をしています。
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

※ 以降で見るDjangoのコードは、[4.0](https://github.com/django/django/tree/4.0)のものを対象としています。

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

        # Request goes through middleware.
        # django.core.handlers.base.BaseHandler.get_response()を呼び出す
        response = self.get_response(request)
```

※ `BaseHandler.get_response()`はDjango本体の処理でテストコードとは離れてしまうので、出力だけを見ておきます。

テストのために色々と処理は書かれていますが、どうやらレスポンスそのものはDjango本体の処理からつくり出されているようです。
より具体的には、`self.get_response()`から、`<HttpResponse status_code=200, "text/html; charset=utf-8">`のようなHttpResponseオブジェクトがつくられています。

ということで`Client.request()`に目を向けると、ここでつくられるレスポンスは、Djangoが返してくれたレスポンスへテンプレートやコンテキストの情報を拡張しているようだ、ということが分かります。
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

こうして見ると、レスポンスのテンプレートとコンテキストは、`data`という辞書に設定されたものを見に行っているようです。
ということは、辞書`data`に関わる処理をたどっていけば、テンプレート・コンテキストの実際に指すものが理解できそうです。

数行程度の処理でも中身は中々に複雑なので、じっくりと追っていきましょう。

#### partial



[参考](https://docs.python.org/3/library/functools.html#functools.partial)

```Python
on_template_render = partial(store_rendered_templates, data)
```



テンプレートが描画されたシグナルで設定 シグナルのハンドラでテンプレート・コンテキストを設定。 ハンドラでは、templateが描画されるたびにテンプレート・コンテキストを追加

#### signals

### Template

`django.template.base.Template`

### ContextList

`django.test.utils.ContextList`, `django.template.context`

## Clientから得られるレスポンスをpytestでも検証したい



