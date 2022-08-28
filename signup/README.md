# 概要

Djangoでユーザ登録アプリをつくってみます。

## ゴール

Djangoが用意しているModelの概要を理解し、データベースを少し操作してみることを目指します。

## 目次

[toc]

## 用語整理

* Model: 
* ORM(Object Relational Mapper): 
* Migration: 

## つくりたいもの

今回つくるのは、ユーザ名をデータベースに登録して別の画面で表示する機能です。具体的な動きをキャプチャから見ておきます。

![image](https://user-images.githubusercontent.com/43694794/186659644-0106143e-9ba0-49c7-a381-24730c6d7606.png)
図1: ユーザ登録画面

![image](https://user-images.githubusercontent.com/43694794/186659807-41470537-0aff-41a3-84b9-c811ba96a130.png)
図2: ユーザ登録結果画面

ユーザ情報をデータベースを介して登録/参照していくことで、Djangoでデータベースを操作するときの一連の流れをたどっていきます。


## プロジェクト・app

前準備としてDjangoアプリケーションの土台となるプロジェクト・appをつくっていきます。
やることはHello World・おみくじアプリケーションと同じなので、概要だけを載せておくに留めます。

```bash
# プロジェクト・appを作成
$ django-admin startproject config .
$ django-admin startapp signup
```

```python
# INSTALLED_APPSへ追記
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
    'signup.apps.SignupConfig',
]
```


## データベース整備

データベースを扱うアプリケーションでは、どのようなデータを参照・保存するのかあらかじめ決めておくことが重要です。ユーザ登録機能では、ユーザ情報として何を保存して何を表示するのか決めておけば、迷うことなく開発が進められそうです。
よって、まずはユーザ情報を保存するデータベースのテーブルをつくっておこうと思います。

最初に、データベースを組み立てるためのDjangoの機能にどのようなものがあるのか、概略を見ていきます。概念を押さえたあとで手を動かしながらユーザ登録機能を実現するのに必要なものを用意していきます。

### Model

Djangoでは、データベースと関わりの深い要素にModelと呼ばれるものがあります。DjangoのModelは、アプリケーションのデータを保管・表現するものと定義されています。

[参考](https://docs.djangoproject.com/en/4.1/topics/db/models/)

これだけでは実体が見えてこないので、ユーザ情報を表現するModelを先取りして見ておきます。

```python
# Djangoが提供するModel機能を表現したパッケージ
from django.db import models

# ユーザ情報を表現するModel
class User(models.Model):
    """ ユーザ情報を表現することを責務に持つ """
    username = models.CharField(max_length=255)
```

ユーザ名を属性として持たせたクラスをつくることで、ユーザ情報を表しています。加えてModelは、クラス名をデータベースのテーブルと・属性をテーブルのカラムと対応づけています。
言い換えると、Modelはアプリケーションで扱うデータが何であるかを記述したものだと捉えることができます。

ここではひとまず、DjangoがModelを軸にデータベースと連携するさまざまな機能を用意してくれているんだな、ということを覚えておきましょう。

#### 補足: DjangoのModelとMVCのModelの関係

DjangoのModelとMVCモデルのM(Model)は同じ単語で表現されています。DjangoのModelが意味するところをより深く理解するためにも、MVCのModelが指すものとの関係を整理しておきます。

[参考](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller)

MVCモデルのModelは、アプリケーションにおけるデータ・ロジック・規則を管理するものと定義づけられています。
何やら捉えづらい表現になってしまったので、英単語Modelの意味と照らし合わせてみます。英単語Modelは、ある事物を擬似的に再現したものを意味します。

[参考](https://dictionary.cambridge.org/dictionary/english/model)

スケジュール管理アプリケーションを例に考えてみましょう。これは、現実世界のスケジュール帳を擬似的に再現したものと言い換えることができます。
スケジュール帳をアプリケーションで実現するのであれば、プログラム上でスケジュールを表すデータをつくったり、スケジュールを記録する処理をつくることになります。これらのデータ・ロジックがMVCモデルのModelに相当します。
つまり、MVCモデルのModelは、アプリケーションでModel化する対象をプログラムで表現したものと言えます。

---

こうして見ると、DjangoのModelとMVCモデルのModelはずいぶん違ったものに見えます。後者はデータを保存するだけでなく、ロジックや規則も含んだより広いものを指していそうです。
それではなぜDjangoはアプリケーションのデータを表現する機構にModelという名前を付けたのでしょうか。
おそらく、Djangoというフレームワークがつくる骨組みのうち、MVCモデルのModelに関わるものをデータベースに限定したからだと思われます。データベース操作を責務に持つモジュールをModelと命名することで、DjangoにおけるModelの範囲を明確にできる、というのもあったのではないかと考えられます。


### Migrations

DjangoのModelは、アプリケーションで扱うデータを表現したものであることが分かりました。それならば、Modelをもとにデータベースへ対応するテーブルをつくってくれるような機能が欲しくなるところです。
そこで、DjangoではModelの情報をデータベースへ反映する`migration`という機能を用意してくれています。

[参考](https://docs.djangoproject.com/en/4.1/topics/migrations/)



### データベース環境構築


## ユーザ登録画面

### ユーザ登録処理

### PRGパターン

## ユーザ登録結果画面

### ユーザ情報取得

#### 補足: なぜModelではフィールドをクラス属性に定義するのか

### ユーザ情報表示

## まとめ


Djangoでユーザ登録アプリをつくりたい。

https://docs.djangoproject.com/en/4.0/topics/db/models/#models-across-files

TODO データベース操作(レコード挿入)はfixtureをimportして実現できるか試したい

おみくじとの差分
* Modelを新しくつくる(makemigration, migrate)
* ユーザModelはメールアドレス + ユーザ名
* Modelを操作(表示・登録)
* POSTボディを参照するようになった

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
```

```bash
$ python manage.py migrate
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying sessions.0001_initial... OK

```

ユーザModelの登録

```bash
$ python manage.py makemigrations signup
Migrations for 'signup':
  signup/migrations/0001_initial.py
    - Create model User
```

```bash
$ python manage.py migrate
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, signup
Running migrations:
  Applying signup.0001_initial... OK
```