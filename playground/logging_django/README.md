# 概要

Djangoでログ出力を試してみたい。

## ゴール

DjangoがどのようにLoggerを設定しているのか・Djangoアプリケーションでどのようにログを出力したらよいのか概要を理解することを目指す。

## DjangoのLogger

ここでは、Djangoがどのようにログ出力を実現しているのか見てみる。

### 出力方法

デフォルトではPythonのloggingライブラリを利用し、dictConfigでLoggerを生成している。
設定値はsettings.pyへ定義するようになっており、setup処理でLoggerが設定される。

### 設定値

上書きしない限りは、settings.pyのLOGGING属性へ定義した辞書とデフォルト値の辞書がマージされる。

[参考](https://github.com/django/django/blob/main/django/utils/log.py)

全体像を掴んでおくため、デフォルトの設定をざっと見ておく。

```Python
DEFAULT_LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] {message}",
            "style": "{",
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "mail_admins"],
            "level": "INFO",
        },
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
```

#### console

Djangoの各種ログをコンソールへ出力するためのHandler。
ログレベルINFO以上が設定されているので、ここで出力されるものはあまり多くない。

#### django.server

いわゆる開発サーバの出力を捕捉するためのLogger/Handler。
runserverコマンドでサーバを起動した場合のみ参照される。

#### mail_admins

ログレベルERROR以上のメッセージを管理者メールアドレスへ通知するためのHandler。

#### デフォルトのLogger(django・django.server)の違いは何か

`django`はDjangoにおけるroot Loggerの位置付け。
`django.server`は開発サーバで記録されるログを対象としたLoggerである。

このようにしておくことで、`django`は子のLoggerから伝播した重要度の高いメッセージを捕捉できるようになる。


## 本番用っぽい設定をつくりたい

Djangoのデフォルトの設定値は本番運用には向かないようなので、カスタマイズしてみる。
設定値は`現場で使える Django の教科書《基礎編》`を参考にした。

```Python
# settings.py
# LOGGING_CONFIG属性をNoneとしておくと、DjangoによるLogger設定処理がスキップされる
LOGGING_CONFIG = None

# 自前のLoggerを定義
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

大まかな方針は、以下の通りである。

* アプリケーションのログはapp.logへ記録
* DjangoのログはログレベルINFO以上を記録しておく こうすることで、Djangoから通知される一定以上の重要度のログを捕捉できる

つまり、Django・アプリケーションそれぞれでログを共存させている。

### リクエスト・レスポンスをログへ出力したい

アプリケーションで実際にログを出力してみる。今回はリクエスト・レスポンスをviews.pyから書き出す程度に留める。

```Python
# views.py
import logging
from django.http import HttpRequest, HttpResponse

# アプリケーション用のLoggerを生成
logger = logging.getLogger(__name__)


def get(request: HttpRequest) -> HttpResponse:
    """
    ログへ記録するリクエスト・レスポンスを処理

    :param request: HTTPリクエスト
    :return: HTTPレスポンス
    """

    # リクエストを記録
    logger.info('%s %s REQUEST', request.method, request.path_info)

    response = HttpResponse('Log')
    # レスポンスを記録
    logger.info('%s %s %s RESPONSE', request.method, request.path_info, response.status_code)
    return HttpResponse(response)
```

このように記述した上でレスポンスを得ると、以下のようなログが出力される。

```bash
# app.log sample
2022-05-02 00:55:05,639 [INFO] /logging_django/src/log_sample/views.py:15 GET / REQUEST
2022-05-02 00:55:05,639 [INFO] /logging_django/src/log_sample/views.py:17 GET / 200 RESPONSE
```
 

## 開発用っぽい設定をつくりたい

今度は開発用の設定をつくってみる。
今回は実験用にすべてコンソールへ出力しているが、場合によってはファイルへ書き出しておくのもよさそう。

```Python
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
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'app'
        },
    },

    # ロガー
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False
        },
        # SQL文を出力
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        }
    },
})
```

本番用との大きな違いは、Handlerをコンソール用としたことである。また、開発環境では実行されたSQL文を見られるようにする設定も加えた。

### SQLをログへ出力してみたい

アプリケーションで実行されたSQLをログへ出力してみる。

```Python
import logging
from django.http import HttpRequest, HttpResponse

from .models import Sample

logger = logging.getLogger(__name__)


def get(request: HttpRequest) -> HttpResponse:
"""
ログへ記録するリクエスト・レスポンスを処理

    :param request: HTTPリクエスト
    :return: HTTPレスポンス
    """

    logger.info('%s %s REQUEST', request.method, request.path_info)

    # SQLがログへ出力されるか検証用
    sample = Sample.objects.get(text='hello')

    response = HttpResponse('Log')
    logger.info('%s %s %s RESPONSE', request.method, request.path_info, response.status_code)
    return HttpResponse(response)
```

```bash
# sample ※ 見やすくなるように改行を追記
2022-05-02 01:05:52,317 [DEBUG] /.local/share/virtualenvs/django-yw3ov-AL/lib/python3.9/site-packages/django/db/backends/utils.py:124 \
(0.000) SELECT "log_sample_sample"."id", "log_sample_sample"."text" FROM "log_sample_sample" WHERE "log_sample_sample"."text" = 'hello' \ 
LIMIT 21; args=('hello',); alias=default
```

コンソールへSQLが出力された。


#### DjangoのLoggerはどうカスタマイズしていくべきか

開発するときを除いて、デフォルトのLoggerはDBから発行されるSQLを記録する程度に留めた方が良さそう。
基本はアプリ側で制御し、Djangoのログは必要に応じて収集する設定を加えるようにするのがよいか。

この辺りは色々運用しながら考えたい。
