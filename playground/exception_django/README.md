# 概要

Djangoの基本的な例外処理を試してみる。

## ゴール

Djangoアプリケーションで予期しない問題が発生したとき、ログに記録したりユーザへ通知できるような方法を理解することを目指す。

## 404ページ

最初に、存在しないURLへのリクエストを404ページのレスポンスで処理する方法を調べてみる。

[参考](https://docs.djangoproject.com/en/4.0/topics/http/views/#customizing-error-views-1)

どうやらURLconfの任意の箇所へ`handler404`という属性を定義し、404ページのレスポンスを返却するviewを指定すればよいようだ。

また、ページは存在するがリソースは存在しないようなリクエスト(例: ブログの記事へのリクエストでパスからDBを検索するようなもの)を404レスポンスで扱いたい場合は、
Http404例外を送出するとよい。

[参考](https://docs.djangoproject.com/en/4.0/topics/http/views/#the-http404-exception)

### 404.htmlを表示させたい

実際に404ページを表示させてみる。
※ settings.pyのDEBUG属性が有効だとDjangoが設定したページが強制的に表示されるので、検証したい場合は一旦無効にしておく。

#### URLconf

URLconfへ404レスポンスのハンドラへの参照を追加。

```Python
# urls.py
from django.urls import path

from .views import get, handle_404

handler404 = handle_404

urlpatterns = [
    path('', get),
]
```

あわせて、views.pyへハンドラを記述しておく。

```Python
# views.py
import logging

from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import render

def handle_404(request: HttpRequest, e: Http404) -> HttpResponse:
    """
    404エラー画面描画

    :param request: HTTPリクエスト
    :param e: 404エラー
    :return: 404エラー用の画面を表現するHTTPレスポンス
    """
    return render(request, 'errors/404.html')

def get(request: HttpRequest) -> HttpResponse:
    """
    通常の画面描画
    
    :param request: HTTPリクエスト
    :return: テスト用の画面を表現するHTTPレスポンス
    """
    return render(request, 'hello.html')
```

404ページのHTMLファイルは他のテンプレートと同じように扱うことができる。

![image](https://user-images.githubusercontent.com/43694794/166206748-ed2d2e4d-0798-4eb8-a8bf-2db2f6295d4b.png)

適当なHTMLファイルをつくり、適当なURLへアクセスすると、404ページのレスポンスが得られた。

#### Djangoはどのような仕組みでhandler404を呼び出しているのか

とりあえずドキュメントに従うことで期待通りの結果は得られた。しかし、もう少し踏み込んで、なぜこのように書くことで動作するのか概略を知っておきたい。

Djangoにおいて、各リクエストを処理する関数は、`django/core/handlers/exception.py`に定義された`convert_exception_to_response()`でラップされている。
これは処理の内部で例外(対象はExceptionクラス)が送出されると、同ファイルの`response_for_exception()`を呼び出す。当該箇所では更に`get_exception_response()`が呼ばれる。
そして、`django/urls/resolvers.py`の`resolve_error_handler()`から、`handle404`という属性に定義された関数を呼び出す。

以上の流れにより、handler404が呼び出されている。

※ Http404例外は、URLからview関数を解決するときに、サブクラスのResolver404を対象に送出されている。

## 500ページ

予期しない例外を捕捉する手段も調べてみる。

Djangoでは、予期しない例外はすべて500エラーとして扱う。

[参考](https://docs.djangoproject.com/en/4.0/ref/views/#the-500-server-error-view)

これは、ただページを表示するだけであれば、404エラーと同じように扱うことができる。ひとまずはページを表示するところまで動かしてみる。

### 500.htmlを表示したい

404エラーと同じようにurlConf・viewへ設定。

```Python
# urls.py
from django.urls import path

from .views import get, raise_exception, handle_404, handle_500

handler404 = handle_404
handler500 = handle_500

urlpatterns = [
    path('', get),
    path('invalid', raise_exception)
]
```

```Python
def raise_exception(request: HttpRequest) -> HttpResponse:
    """
    サーバエラーを擬似的に再現

    :param request: HTTPリクエスト
    :return: テスト用の画面を表現するHTTPレスポンス
    """
    try:
        # なにかの処理
        raise SampleException()
    except SampleException as e:
        raise
    return render(request, 'hello.html')


def handle_500(request: HttpRequest) -> HttpResponse:
    """
    500エラー画面描画

    :param request: HTTPリクエスト
    :return: 500エラー用の画面を表現するHTTPレスポンス
    """
    return render(request, 'errors/500.html')
```

![image](https://user-images.githubusercontent.com/43694794/166206677-64800559-b443-402b-8b11-2b0714aeb815.png)

画面が表示されたことを確認。
また、呼び出し先で例外を処理するとロジックが重複するおそれがあることから、ログに記録したら以降の処理はDjangoへ委譲しておく。

### ログ出力設定を追加したい

これだけでは実用に向かないので、ログ出力処理を追加してみる。
DjangoのLoggerでもある程度の情報は得られるが、サマリに相当するものでしかないので、アプリケーション側でもログ出力処理を記述しておく。
こうすることで、例外が発生したときの詳細な文脈をたどれるようになる。

#### Logger

settings.pyへLoggerを生成する処理を追記。デフォルトのLogger設定ではアプリケーションのログを捕捉できないので、上書きしておく。

```Python
# settings.py
LOGGING_CONFIG = None
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,

    # フォーマット
    'formatters': {
        'app': {
            'format': '%(asctime)s [%(levelname)s] %(pathname)s:%(lineno)d %(message)s'
        }
    },

    # ハンドラ
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': './logs/app.log',
            'formatter': 'app'
        },
        'django_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': './logs/django.log',
            'formatter': 'app'
        },
    },

    # ロガー
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django': {
            'handlers': ['django_file'],
            'level': 'INFO',
            'propagate': False
        }
    },
})
```

#### view

viewで例外処理の前後にログ出力処理を追記してみる。

```Python
# views.py
import logging

from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import render

from .exceptions import SampleException

logger = logging.getLogger(__name__)


def raise_exception(request: HttpRequest) -> HttpResponse:
    """
    サーバエラーを擬似的に再現

    :param request: HTTPリクエスト
    :return: テスト用の画面を表現するHTTPレスポンス
    """
    logger.info('raise exception')
    try:
        # なにかの処理
        raise SampleException()
    except SampleException as e:
        logger.exception('SampleException %s %s %s', request.method, request.path_info, request.headers)
        raise
    return render(request, 'hello.html')
```

```bash
# ログのサンプル
2022-05-02 07:14:48,575 [INFO] /exception_django/src/exception_sample/views.py:28 raise exception
2022-05-02 07:14:48,575 [ERROR] /exception_django/src/exception_sample/views.py:33 SampleException GET /invalid {'Content-Length': '', 'Content-Type': 'text/plain', 'Host': 'localhost:8000', 'Connection': 'keep-alive', 'Cache-Control': 'max-age=0', 'Sec-Ch-Ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"', 'Sec-Ch-Ua-Mobile': '?0', 'Sec-Ch-Ua-Platform': '"macOS"', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Sec-Fetch-Site': 'none', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-User': '?1', 'Sec-Fetch-Dest': 'document', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-US,en;q=0.9,ja;q=0.8', 'Cookie': 'Pycharm-eab1ba27=f3eb943d-1a7b-46b6-9a00-45f0a918ff34; Pycharm-eab1ba28=5a563732-eb3a-4d19-8524-9f393313f4bd; Webstorm-4e838afe=430901d1-0b1b-44ef-ac5d-6a75dac31f4a; Pycharm-eab1ba29=7c703e27-e59e-4147-a69d-f11c455b996a; csrftoken=ByJtQLvAGSOGhgdfoFehVlpKlNCeOaCd4XgzRucogGcExWRerXKNOWZ5BvXQTC3O'}
Traceback (most recent call last):
  File "/exception_django/src/exception_sample/views.py", line 31, in raise_exception
    raise SampleException()
exception_sample.exceptions.SampleException
```

`logger.exception()`を利用することで例外情報も記録できた。

#### 500エラーはどのようにDjangoで捕捉されるのか

これも404エラーと仕組みはほぼ同じ。
リクエストを処理する関数を例外ハンドラでラップし、既定のどの例外にも当てはまらなかったものが500エラーとして扱われる。
