# 概要

Djangoでユーザ登録アプリをつくってみます。

## ゴール

Djangoが提供しているModelの概要を理解し、データベース操作へ入門してみることを目指します。
※ 以降ではデータベースが指すものをリレーショナルデータベースに限定します。

## 目次

[toc]

## 用語整理

* Model: Djangoにおいては、アプリケーションで扱うデータを表現したもの
* Migration: 移住を意味し、DjangoではModelの変更をデータベースへ反映することを指す

* ORM(Object Relational Mapper): 

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
# ユーザ登録アプリなのでsignupと命名
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


## データベース整備-前準備

データベースを扱うアプリケーションでは、どのようなデータを保存・参照するのかあらかじめ決めておくことが重要です。ユーザ登録機能では、ユーザ情報として何を登録して何を表示するのか決めておけば、迷うことなく開発が進められそうです。
よって、まずはユーザ情報を保存するデータベースのテーブルをつくることから始めます。

最初に、データベースを組み立てるためのDjangoの機能にどのようなものがあるのか、概略を見ていきます。概念を押さえたあとは、手を動かしながらユーザ登録機能に必要なものを用意していきます。

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

ユーザ名を属性として持たせたクラスをつくることで、ユーザ情報を表しています。加えてModelは、クラス名をデータベースのテーブル・属性をテーブルのカラムと対応づけています。
言い換えると、Modelはアプリケーションで扱うデータが何であるかを記述したものだと捉えることができます。

ここではひとまず、DjangoがModelを軸にデータベースと連携するさまざまな機能を用意してくれているんだな、ということを覚えておきましょう。

#### 補足: DjangoのModelとMVCのModelの関係

DjangoのModelとMVCモデルのM(Model)は同じ単語で表現されています。DjangoのModelが意味するところをより深く理解するためにも、MVCのModelが指すものとの関係を整理してみます。

[参考](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller)
[参考2](https://stackoverflow.com/questions/5863870/how-should-a-model-be-structured-in-mvc)

MVCモデルのModelは、アプリケーションにおけるデータ・ロジック・規則を管理するものと定義づけられています。
あわせて、英単語Modelの意味も見てみます。英単語Modelは、ある事物を擬似的に再現したものを意味します。

[参考](https://dictionary.cambridge.org/dictionary/english/model)

定義だけではイメージが掴みづらいので、スケジュール管理アプリケーションを例に考えてみましょう。これは、現実世界のスケジュール帳を擬似的に再現、すなわちModel化したものと言い換えることができます。
スケジュール帳をアプリケーションで実現するのであれば、プログラム上でスケジュールを表すデータをつくったり、スケジュールを記録する処理をつくることになります。これらのデータ・ロジックがMVCモデルのModelに相当します。
つまり、MVCモデルのModelは、アプリケーションでModel化する対象をプログラムで表現したものと言えます。

---

こうして見ると、DjangoのModelとMVCモデルのModelはずいぶん違ったものに見えます。後者はデータを保存するだけでなく、ロジックや規則も含んだより広いものを指していそうです。
それでは、なぜDjangoはアプリケーションのデータを表現する機構にModelという名前を付けたのでしょうか。
明確に言及されていないので推測となりますが、Djangoというフレームワークがつくる骨組みのうち、MVCモデルのModelに関わる機能をデータベースに限定したからだと思われます。
これは、図3のようなイメージです。

![image](https://user-images.githubusercontent.com/43694794/194554806-6618a2ce-2a87-4996-aa0e-51da4da8b99f.png)

図3: Django・MVC Modelそれぞれのイメージ

データベースから得られたデータを扱うロジックやルールは、アプリケーションに固有のものなので、フレームワークが提供するModelの要素に含まれないのも頷けます。

話が少し難しくなってしまいましたが、Modelという抽象的な単語をさまざまな側面で比較してみることで、DjangoにおけるModelが何を指しているのか少しでも見えてくれば幸いです。


### Migrations

DjangoのModelは、アプリケーションで扱うデータを表現したものであることが分かりました。それならば、Modelからデータベースの対応するテーブルをつくってくれるような機能が欲しくなるところです。ModelとデータベースをDjangoが対応づけてくれれば、それぞれが乖離することもなくなりそうです。
そこで、DjangoではModelの情報をデータベースへ反映する`migration`という機能を用意してくれています。

[参考](https://docs.djangoproject.com/en/4.1/topics/migrations/)

migrationそのものの概要を復習しておきたい場合は、[参考リンク](https://martinfowler.com/articles/evodb.html#AllDatabaseChangesAreMigrations)を見てみてください。

Djangoのmigration機能は、2つの管理コマンドによって実現されます。
Modelをデータベースへ反映するためのファイル(migrationファイル)を`makemigrations`コマンドでつくり、`migrate`コマンドでデータベースへ反映します。

#### 補足: なぜ`makemigrations`コマンドが必要なのか

Modelをデータベースへ反映させるのであれば、`migrate`コマンド1つで十分なように思えます。なぜわざわざ`makemigrations`コマンドでファイルをつくるのでしょうか。
これは、データベースへの変更内容をファイルで残し、バージョン管理するためです。
`makemigrations`コマンドでつくられたファイルがあれば、アプリケーションのデータベースを任意の状態・任意の環境で組み立てられるようになります。
つまり、バージョン管理されたファイルを通じてほかのチームメンバーやテスト環境など・異なる環境へ簡単に展開することができます。


## データベース環境構築

さて、Djangoでデータベースを利用するときに目にする主要な機能をざっくりと見てきました。ここからは知識を手に馴染ませるために実際にデータベース・テーブルをつくってみます。
ゴールとして、ユーザ情報を表現するデータベースのテーブルをつくることを目指していきましょう。

### 接続設定

最初に、今回つくるデータベースの概要を掴んでおきます。
といっても入門段階ではとてもシンプルで、RDBMSの1つであるSQLiteをDjangoが標準で用意してくれています。SQLiteを利用するための設定は、テンプレートと同様`config/settings.py`に書かれています。

```python
# config/settings.py
# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

# データベース関連の設定
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

各種設定値を簡単にみておきましょう。

#### `DATABASES`

設定値は`DATABASES`に辞書形式で書かれています。
[参考](https://docs.djangoproject.com/en/4.1/ref/settings/#databases)

#### `default`

`default`キーは、複数のデータベースを切り替えない限りあまり意識することはないかと思います。
[参考](https://docs.djangoproject.com/en/4.1/topics/db/multi-db/#defining-your-databases)

#### `ENGINE`

`ENGINE`キーは、どんな種類のデータベースを利用するかを記述します。今回はデフォルト値としてSQLite3を設定しておきます。
[参考](https://docs.djangoproject.com/en/4.1/ref/settings/#engine)

#### `NAME`

`NAME`キーはSQLiteに特有のもので、データベースファイルをどこに置くか記述します。特に場所を変える必要もないので、デフォルト値(manage.pyと同階層)としておきます。
[参考](https://docs.djangoproject.com/en/4.1/ref/settings/#name)


### Modelづくり

Djangoアプリケーションでデータベースのテーブルをつくりたい場合は、Modelを組み立てることから始めます。
各種appにはModelを定義するための`models.py`が最初から用意されているので、早速触ってみましょう。

```python
# signup/models.py
from django.db import models

# Create your models here.
```

ModelはPythonのクラスでデータベースのテーブルを表現しています。ですので、ユーザ名を属性に持つことでユーザ情報を表現するクラスをつくってみることにします。このクラスがModelの役割を担います。

[参考](https://docs.djangoproject.com/en/4.1/topics/db/models/)

```python
# signup/models.py
from django.db import models


class User(models.Model):
    """ ユーザ情報を表現することを責務に持つ """
    # ユーザ名カラムを表現する属性
    username = models.CharField(max_length=255)
```

Modelを表現しているクラスで何が書かれているのか、1つずつ読み解いていきましょう。

#### `django.db.models.Model`

まず、クラスそのものは`django.db.models.Model`クラスを継承しています。これによりデータベース操作の大半をDjangoに任せられます。

#### Field

続いて、クラス属性を見てみます。
Modelのクラス属性には何を書いてもいいわけではなく、`Field`と呼ばれるものを定義します。

[参考](https://docs.djangoproject.com/en/4.1/topics/db/models/#fields)

Fieldはテーブルのカラムを表現しており、カラムの型や制約の情報を持ちます。
Djangoでは型に応じてさまざまなFieldを提供しており、単純な文字列を表現するカラムには、`CharField`が用意されています。

[参考](https://docs.djangoproject.com/en/4.1/ref/models/fields/#django.db.models.CharField)

CharFieldは必須の属性として`max_length`を持ち、文字列型のカラムの最大文字数を指定します。ユーザ名はそこまで長くならないはずなので、ひとまず255文字としておきます。

---

ユーザ情報を表現するModelでどのようなことが書かれているのか簡単に見てきました。復習のために、`models.py`に定義したModelが何を表現しているのか言葉にしておきましょう。
クラスUserはデータベースのテーブルと対応しています。クラス属性`username`は最大長が255文字の文字列型のカラムと対応しています。つまり、今回つくられたModelはアプリケーション・データベースでユーザ情報を表現するものであることが分かります。


### migration

Modelができあがったので、Modelの情報からDjangoにデータベースのテーブルをつくってもらいます。
これは、管理コマンド`makemigrations`・`migrate`からなるmigrationの仕組みによって実現できます。以降では、各コマンドを実際に動かしてみます。

#### `makemigrations`コマンド

`makemigrations`コマンドにより、データベースへの変更内容を記したマイグレーションファイルをつくってみます。

[参考](https://docs.djangoproject.com/en/4.1/ref/django-admin/#makemigrations)

> 書式: `django-admin makemigrations [app_label [app_label ...]]`

`app_label`はひとまずappのディレクトリ名(今回はsignup)を指定するものと思っておけば大丈夫です。

※ 書式上は`django-admin`で指定されていますが、`python manage.py`でも同じように書くことができます。サーバ起動などのコマンドとあわせた方がシンプルなので、以降では`python manage.py`の書式で書いていきます。
[参考](https://docs.djangoproject.com/en/4.1/ref/django-admin/)

```bash
$ python manage.py makemigrations signup
# 出力
Migrations for 'signup':
  signup/migrations/0001_initial.py
    - Create model User
```

`signup/migrations`ディレクトリへマイグレーションファイルとして、`0001_initial.py`がつくられたようです。
マイグレーションファイルはDjangoがよしなにやってくれるところではありますが、雰囲気を掴むために中身もざっと見ておきましょう。

```python
# signup/migrations/0001_initial.py
from django.db import migrations, models


# migration情報を表現
class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    # 具体的にどのようにデータベースを変更するか記述
    operations = [
        # Modelを新しく作成
        migrations.CreateModel(
            name='User',
            fields=[
                # 明示的に定義していないもの
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255)),
            ],
        ),
    ]
```

Modelのように、Pythonのクラス形式でどのようにデータベースを変更するか表現しているようです。クラス属性などから、新しくModelをつくることが読み取れます。
ただ、データベースのカラムを表す`fields`と呼ばれる箇所を見てみると、idなる見慣れないものが加わっています。
実はDjangoでは、明示的に主キーを定義しなかった場合、連番形式のカラムidを主キーとして補ってくれます。より具体的なところは、発行されるSQLを見ることで雰囲気が掴めるはずです。

[参考](https://docs.djangoproject.com/en/4.1/topics/db/models/#automatic-primary-key-fields)

#### `sqlmigrate`コマンド

あとは`migrate`コマンドでModelをデータベースへ反映してもらうだけです。ですがこれだけでは裏側のSQLがすべて隠れてしまっているので、何が起こっているのか見えづらいです。
そこで`sqlmigrate`なるコマンドから、`migrate`コマンドが実行してくれるSQLを覗いておきましょう。

[参考](https://docs.djangoproject.com/en/4.1/ref/django-admin/#sqlmigrate)

> 書式: `django-admin sqlmigrate app_label migration_name`

`app_label`引数にはappの名前として`signup`を・`migration_name`引数には拡張子を除いたマイグレーションファイル名を指定します。

```bash
$ python manage.py sqlmigrate signup 0001_initial

# 実行されるSQL
# --以降はコメント
BEGIN;
--
-- Create model User
--
CREATE TABLE "signup_user" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "username" varchar(255) NOT NULL);
COMMIT;
```

発行されるSQLを確認してみると、`CREATE TABLE`文でユーザ情報を表現するテーブルをつくってくれるようです。

また、テーブル名はほかと重複しないよう、appの名前とModelのクラス名をスネークケース形式で記述した規則にて設定されます。
[参考](https://docs.djangoproject.com/en/4.1/ref/models/options/#table-names)

#### `migrate`コマンド

migrationによりどんなSQLが実行され、どのようにデータベースが変更されるのか見えてきました。
全容が見えてきたところで、いよいよデータベースへテーブルをつくってみます。

[参考](https://docs.djangoproject.com/en/4.1/ref/django-admin/#django-admin-migrate)

> 書式: `django-admin migrate [app_label] [migration_name]`

`sqlmigrate`コマンドとは違い、`app_label`や`migration_name`が省略できるようです。初回ということで、特に引数は指定せずに動かしてみます。

```bash
$ python manage.py migrate

Operations to perform:
  # 最後のsignupがユーザ登録app
  Apply all migrations: admin, auth, contenttypes, sessions, signup
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
  # ユーザ登録のmigration
  Applying signup.0001_initial... OK
```

先ほどつくったユーザ登録app以外にもたくさんの内容が出力されました。これは一体何を表しているのでしょうか。`migrate`コマンドで引数を指定しない場合、`settings.py`の`INSTALLED_APPS`に書かれたすべてのappのマイグレーションファイルがデータベースへ反映されます。
ひとまずは、ここではDjangoが用意してくれていたマイグレーションファイルもデータベースへ反映したんだな、ということだけ押さえておきましょう。
※ 以降では、Djangoが標準で用意しているマイグレーションファイルはプロジェクトをつくるときに反映することにします。

データベースを見てみると、確かに`migrate`コマンドによりデータベースへテーブルがつくられていました。

![image](https://user-images.githubusercontent.com/43694794/188301821-15673ac4-9209-4c47-842e-f8be1ac885f6.png)

また、本命のユーザ情報を表現するテーブル`signup_user`も期待通りの形にできあがっていました。

![image](https://user-images.githubusercontent.com/43694794/188301831-d853e943-5893-4d2b-9392-58222f097f91.png)


---

ようやく最初にゴールとして掲げていた、ユーザ情報を表現するデータベースのテーブルをつくるところまでたどり着けました。
たくさんの用語やコマンドが出てきましたが、一度にすべてを理解しようと思うとしんどくなってしまいます。データベースはこれからたくさん触っていくので、少しずつ身につけていきましょう。


## ユーザ登録画面

![image](https://user-images.githubusercontent.com/43694794/186659644-0106143e-9ba0-49c7-a381-24730c6d7606.png)
図4: ユーザ登録画面(再掲)

土台が出来上がったので、いよいよユーザ登録機能をつくっていきます。
まずは入り口となるユーザ登録画面から始めます。テンプレートの復習がてら、画面を表示するところまで通していきましょう。

### テンプレートの設定

ディレクトリ構成をシンプルにするために、プロジェクトの階層(manage.pyファイルやappディレクトリがあるところ)へテンプレートをつくっていきます。
まずはテンプレート用のディレクトリを新しくつくります。

```bash
$ ls
__init__.py config      db.sqlite3  manage.py   signup
# appやconfigディレクトリと同じ階層にtemplatesディレクトリを作成
$ mkdir templates
```

そして、新しくつくったディレクトリをDjangoが見つけられるよう、テンプレートの設定値に当該ディレクトリを書き加えます。

```python
# config/settings.py
# 中略...
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# 中略...
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 追加
        # テンプレートを探しに行く場所
        # appやconfigと同じ階層につくったtemplatesディレクトリが対象となる
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': False,
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

### ユーザ登録-テンプレート

テンプレートの置き場所ができあがったので、さっそくユーザ登録画面を表すHTMLファイルをテンプレートとしてつくっていきます。


```HTML
<!-- templates/index.html -->
<!DOCTYPE html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, height=device-height, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=M+PLUS+1p:wght@500&display=swap" rel="stylesheet">
    <title>ユーザ登録</title>
</head>
<style>
    body {
        font-family: 'M PLUS 1p', sans-serif;
    }
</style>
<body class="overflow-hidden w-full h-screen bg-sky-400">
<form method="post" action="#" class="mx-auto mt-40 w-3/6 h-4/6 bg-white rounded-3xl">
    <h2 class="pt-24 text-6xl tracking-wider text-center text-slate-500">
        ユーザ登録
    </h2>

    <input
        type="text"
        name="username"
        placeholder="username"
        class="block pl-4 mx-auto mt-24 w-7/12 h-16 rounded-xl bg-slate-100"
    >

    <input
        type="submit"
        value="登録"
        class="block mx-auto mt-16 w-4/12 h-24 text-6xl tracking-wider text-white bg-sky-300 rounded-xl cursor-pointer hover:bg-sky-500"
    >

</form>
</body>
</html>
```

テンプレートで何が書かれているのかざっくりと見ておきます。

#### form

ユーザ情報をアプリケーションへ送るために、form要素を定義しています。
今の段階ではDjangoに特有の書き方はないので、ひとまずテンプレートではユーザ名をPOSTリクエストで送るための土台がつくられていることを押さえておきましょう。

### 画面表示

URLから対応するテンプレートにもとづく画面を表示するために、URLconf, viewを組み立てます。

#### view

最初に画面を表現するHTTPレスポンスを返すviewを見ておきます。`render()`により先ほどつくったテンプレートをもとに、HTTPレスポンスを構築しています。`render()`の記法には後ほど触れます。

```python
# signup/views.py
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse


def index(request: HttpRequest) -> HttpResponse:
    """
    トップ画面
    :param request: HTTPリクエスト
    :return: トップ画面のテンプレートから組み立てられたHTTPレスポンス
    """
    return render(request, 'index.html')
```

#### render()

HTTPレスポンスを組み立てるのに`render()`なる関数を呼び出しました。
これは、よくある処理を簡単に記述するためにDjangoが用意している機能です。書式から使い方を見ておきましょう。

> 書式: `render(request, template_name, context=None, content_type=None, status=None, using=None)`

[参考](https://docs.djangoproject.com/en/4.2/topics/http/shortcuts/#render)

HTTPResponseクラスのイニシャライザ・`render_to_string()`を組み合わせていた処理が関数1つで書けるようになりました。

#### URLconf

特定のURLへのリクエストからviewのindex関数を呼び出すために、対応関係を表現するURLconfを書いていきます。
appで定義したviewに対応づけるために、プロジェクト・appそれぞれでURLconfを定義します。

```python
# signup/urls.py
# 新規作成
from django.urls import path

from .views import index

app_name = 'ユーザ登録'

urlpatterns = [
    # 第1引数にURLのパス要素, 第2引数にview関数そのもの・第3引数に名前付きURLを指定
    # こうすることでURLとviewを対応づけることができる
    path('', index, name='トップ'),
]
```

```python
# config/urls.py
from django.contrib import admin
# include関数を追加
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # 追加
    # appユーザ登録のURLconfを参照するための設定
    path('signup/', include('signup.urls'))
]
```

以上でURLからテンプレートにもとづく画面を描画する準備する準備が整いました。開発サーバを動かして画面が表示されるか見ておきましょう。
開発サーバは、`python manage.py runserver`コマンドで起動することができます。

```bash
$ python manage.py runserver
# 中略...
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

`http://localhost:8000/signup/`へアクセスすることで、ユーザ登録画面が表示されるはずです。

### ユーザ登録処理

ユーザ登録画面を表示するところまでたどり着けました。
ここからはデータベースへユーザ情報を新たに追加する処理をつくっていきます。

#### テンプレート

最初に、ユーザ登録画面のテンプレートにて、ユーザ登録処理へPOSTリクエストを送るための準備をします。
より具体的には、formのaction属性と、POSTリクエストで送る要素へDjangoのテンプレートタグを付け加えます。言葉だけではどう変わるか見えづらいので、実際のテンプレートからどのように変わったのか眺めておきます。

```HTML
<!-- templates/index.html -->
<!-- formタグ内のみ抜粋 -->

<!-- action属性をurlテンプレートタグへ変更 -->
<form method="post" action="{% url 'ユーザ登録:登録' %}" class="mx-auto mt-40 w-3/6 h-4/6 bg-white rounded-3xl">
    <h2 class="pt-24 text-6xl tracking-wider text-center text-slate-500">
        ユーザ登録
    </h2>

    <!-- inputタグが並んでいる箇所へテンプレートタグを追加 -->
    {% csrf_token %}

    <input
        type="text"
        name="username"
        placeholder="username"
        class="block pl-4 mx-auto mt-24 w-7/12 h-16 rounded-xl bg-slate-100"
    >

    <input
        type="submit"
        value="登録"
        class="block mx-auto mt-16 w-4/12 h-24 text-6xl tracking-wider text-white bg-sky-300 rounded-xl cursor-pointer hover:bg-sky-500"
    >

</form>
```

formのaction属性は、おみくじアプリで利用した[url テンプレートタグ](https://docs.djangoproject.com/en/4.1/ref/templates/builtins/#url)で定義しています。引数に名前付きURLを指定することで、URLconfをもとに対応するURLへ変換してくれます。
そして、もう1つ`csrf_token`なるテンプレートタグが加わりました。

[参考](https://docs.djangoproject.com/en/4.1/ref/templates/builtins/#csrf-token)

これは、セキュリティ攻撃の1つである[Cross-site request forgery](https://www.squarefree.com/securitytips/web-developers.html#CSRF)を防ぐための役割を持ちます。
localhostで動かしている間は攻撃されることもありませんが、Djangoではformから送られるすべてのPOSTリクエストにテンプレートタグ`csrf_token`を強制しています。

[参考](https://docs.djangoproject.com/en/4.1/ref/csrf/)

つまり、テンプレートタグ`csrf_token`を書かなければ、下図のようにPOSTリクエストが不正なものとみなされ、403エラーで返されてしまいます。
ひとまずは、DjangoのアプリケーションでformからPOSTリクエストを送るときは、テンプレートタグ`csrf_token`が必要だ、ということを覚えておきましょう。

![image](https://user-images.githubusercontent.com/43694794/190952391-92edcd41-b3ee-456f-995a-f2fdf08417cf.png)

図5: CSRF検証エラー

---

#### 補足: テンプレートタグ`csrf_token`は何を表しているのか

DjangoアプリケーションでPOSTリクエストを送るときは、どうやらテンプレートタグを書き加えなければならないということは分かりました。
しかし、とりあえず必要だからと書くだけでは身につきません。理解を深めるためにも、テンプレートタグ`csrf_token`が具体的に何を表しているのか、実際に描画されたHTMLから見てみましょう。

```HTML
    <!-- templates/index.htmlの描画結果抜粋 -->
    <h2 class="pt-24 text-6xl tracking-wider text-center text-slate-500">
        ユーザ登録
    </h2>

    <!-- {% csrf_token %}の描画結果 -->
    <input type="hidden" name="csrfmiddlewaretoken" value="waQwrMVlvu2d4u5miN7NFnZDu6AAUch0T3MhsOOOO4ghcUjBahUBCVrBHoBUQgge">
```

```HTML
<!-- {% csrf_token %}の描画結果 -->
<!-- もう一度アクセスすると、違う値に変更される -->
<input type="hidden" name="csrfmiddlewaretoken" value="RqWaq2TFOeK7IzQPaWLRSJhEZBVRchouejSVr4M87OYbQZ442qyFPhJCcTWb8lnI">
```

描画されたHTMLを見てみると、テンプレートタグ`csrf_token`は、`csrfmiddlewaretoken`をname属性に持つinput要素をつくってくれるようです。
そして、input要素の値にはランダムな値が設定されています。

#### 補足: `csrfmiddlewaretoken`はどのように参照されるのか

テンプレートタグ`csrf_token`により、POSTリクエストで送るものに`csrfmiddlewaretoken`なるものを加えていることが分かりました。
CSRF攻撃を防ぐためのものであることから、Djangoがよしなに`csrfmiddlewaretoken`を検証しているであろうことが推測できます。
しかし、仕組みが分からないと腑に落ちないので、大まかにでも処理の流れを押さえておきたいところです。

DjangoはCSRF攻撃を防ぐために、`csrfmiddlewaretoken`をいつ・どのように参照しているのでしょうか。

これは、Djangoがリクエスト・レスポンスを処理するときに前処理/後処理として呼ばれるミドルウェアという仕組みが関わっています。

[参考](https://docs.djangoproject.com/en/4.1/topics/http/middleware/)

Djangoが呼び出すミドルウェアは設定ファイルに書かれており、今回のCSRF攻撃に関わるものは、`CsrfViewMiddleware`として定義されています。

```python
# config/settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # CSRF対策用のミドルウェア
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

ミドルウェア`CsrfViewMiddleware`は、リクエスト・レスポンスの前後処理に介入し、以下のような処理をしています。

* formを含むレスポンスを生成するとき、テンプレートタグ`csrf_token`からCSRFトークンを出力
* 検証対象となるCSRFトークンをクッキーで保存
* POSTリクエストを処理するとき、クッキーに保存された値・`csrfmiddlewaretoken`を比較することでリクエストの妥当性を検証

---

少し補足が長くなりましたが、まとめるとDjangoは以下の流れでリクエストを処理することで、CSRF攻撃を防いでいます。

* POSTリクエストを送るformを含む画面を描画するとき、hidden属性のinput要素へ`csrfmiddlewaretoken`を設定
* あわせて、画面を返却するレスポンスへCSRFトークンを含むクッキーを追加

* POSTリクエストが送られると、appのviewなどの処理が呼ばれる前に、ミドルウェア`CsrfViewMiddleware`が呼びだされる
* ミドルウェアにて、リクエストで設定された`csrfmiddlewaretoken`とクッキーに含まれるトークンが一致しているか検証
* 一致していれば安全なPOSTリクエストと判定し、処理を継続 一致しなければ不正なリクエストとして403レスポンスを返却

※ ここでは省略しましたが、厳密には`csrfmiddlewaretoken`は容易に推測されないようmaskingと呼ばれる処理にて、クッキーに設定する値とは異なるものへ変換されています。

#### URLconf

POSTリクエストを画面から送れるようになったので、viewで受け取れるようにします。
まずは入り口として、URLconfへPOSTリクエストのハンドラを登録します。

```python
# signup/urls.py
from django.urls import path

# 更新
# save関数はこれから作成
from .views import index, save

# 追加
# 名前付きURLはapp_nameとviewにつけられた名前(nameキーワード引数)で対応づけられるので、
# app_nameを設定
# ユーザ登録処理は、名前付きURLにて「ユーザ登録:登録」と表現される
app_name = 'ユーザ登録'

urlpatterns = [
    path('', index, name='トップ'),
    # 追加
    path('save', save, name='登録'),
]
```

#### view

実際にリクエストを処理するview関数をつくります。より具体的には、`signup/views.py`へユーザ登録処理を責務に持つ関数`save()`を追加します。

```python
# signup/views.py(抜粋)
def save(request: HttpRequest) -> HttpResponse:
    """
    ユーザ登録処理
    :param request: HTTPリクエスト
    :return: トップ画面のテンプレートから組み立てられたHTTPレスポンス
    """
    user = SaveAction()(request.POST['username'])

    return render(request, 'index.html')
```

重要なのは、`request.POST`を参照している処理です。たった1行の処理ではありますが、たくさんの情報が詰まっているので、少しずつ読み解いていきます。

#### POSTボディ

POSTリクエストで送られたユーザ名は、requestオブジェクトの`POST`という属性に設定されています。

[参考](https://docs.djangoproject.com/en/4.1/ref/request-response/#django.http.HttpRequest.POST)

`request.POST`の実体はPythonの辞書のようなオブジェクトで、大抵の場合は`request.POST['formのname属性']`といった形でPOSTボディへアクセスすることができます。
※ 厳密には辞書を拡張したもので、チェックボックスのような同一のキーで異なる値を持つ要素に対応するための処理などが書かれています。

今回は`request.POST['username']`のように記述することで、formからPOSTリクエストで送られたユーザ名を参照することができます。

#### usecase

残りは、リクエストから得られたユーザ名をもとにユーザ情報をデータベースへ登録するだけです。
短い処理なのでviewに書いてもよいのですが、メンテナンス性やテストコードを書くことを考えて別のモジュールへ切り出すことにします。

モジュールさえ分かれていればよいので、ディレクトリ構成などに制約はありません。
ですがなにか1つ決めなければ先に進めません。よってここでは、アプリケーションに固有のロジックを`usecase`というディレクトリの`actions.py`へ分離させています。
上のコードはActionクラスを呼び出し可能オブジェクトとしたことで、ユーザ登録処理をシンプルに呼び出せるようにしています。

※ モジュールの分け方はあくまでも一例なので、要件や好みに応じて変えてみてください。

[参考](https://en.wikipedia.org/wiki/Use_case)

[参考2](https://zenn.dev/mpyw/articles/ce7d09eb6d8117)

#### ユーザ登録処理(データベース)

いよいよ今回のメインであるデータベースへユーザ情報を登録する処理を見てみます。数行ほどなので、先にコードから雰囲気を探っておきます。
以降にて各コードが何を意味しているのか掘り下げていきます。

```python
# signup/usecase/actions.py
from ..models import User


class SaveAction:
    """ ユーザ登録処理を責務に持つ """

    def __call__(self, username: str) -> User:
        """
        ユーザ情報をDBへ登録
        :param username: 登録ユーザのユーザ名
        :return 登録されたユーザModel
        """
        user = User(username=username)
        user.save()

        return user
```

#### Modelオブジェクト生成

Modelクラスは自身がデータベースのテーブルを・インスタンスがテーブルのレコードを指しています。
よって、User Modelのインスタンスをつくることで、データベースのテーブルへ登録したいレコードを表現するオブジェクトができあがります。

[参考](https://docs.djangoproject.com/en/4.1/topics/db/queries/#creating-objects)

イニシャライザにはキーワード引数で各カラムを表すField名を指定することで、カラムの値を設定することができます。

#### 登録

Modelクラスには、データベースへクエリを発行するための便利なAPIがいくつか用意されています。
`Model.save()`はその1つで、文字通りModel情報をデータベースへ登録します。

[参考](https://docs.djangoproject.com/en/4.1/ref/models/instances/#django.db.models.Model.save)

---

一連の処理を整理すると、最初にデータベースへ登録したいレコードをユーザModelのインスタンスとしてつくりました。
そして、Modelが用意しているAPI`Model.save()`を呼び出すことでINSERT文が発行され、上でつくったレコードが実際にデータベースへ反映されます。

以上の処理により、ユーザ登録画面でユーザ名を含むPOSTリクエストを送ると、データベースへユーザ情報を登録できるようになりました。

![image](https://user-images.githubusercontent.com/43694794/192518229-2bbf285f-3ec0-4bd2-8ae6-4d20227ac493.png)

図7: ユーザ登録処理後のデータベースの状態

## ユーザ登録結果画面

![image](https://user-images.githubusercontent.com/43694794/186659807-41470537-0aff-41a3-84b9-c811ba96a130.png)
図8: ユーザ登録結果画面(再掲)

登録後の画面として、ユーザ登録結果画面をつくります。
ユーザ情報をデータベースへ登録できたところで満足してもよいですが、もう少しModelと仲良くなることを目指してみます。具体的には、Modelを介してデータベースからユーザ情報を取得し、画面に表示できるようにします。

### テンプレート

最初に全体像を掴むために、テンプレートを見ておきます。ユーザ名を画面に表示しているだけなので、これまでの知識で問題なく理解できるはずです。

```html
<!-- templates/result.html -->
<!DOCTYPE html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, height=device-height, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=M+PLUS+1p:wght@500&display=swap" rel="stylesheet">
    <title>ユーザ登録結果</title>
</head>
<style>
    body {
        font-family: 'M PLUS 1p', sans-serif;
    }
</style>
<body class="overflow-hidden w-full h-screen bg-sky-400">
<div class="grid place-content-center mx-auto mt-40 w-3/6 h-4/6 bg-white rounded-3xl">

    <h2 class="text-6xl tracking-wider text-center text-slate-500">
        ようこそ、{{ user.username }}さん
    </h2>
</div>
</body>
</html>
```

肝となるのは、ユーザ名を表示している処理`{{ user.username }}`です。
`user`はUser Modelを表しており、`.`による属性アクセスからカラムの値を参照できます。
つまり、User Modelをコンテキストに上記テンプレートからレスポンスを組み立てる処理をつくれば、ユーザ登録画面を実現できそうです。

以降では、登録されたユーザ情報をデータベースから読み出す処理をつくっていきます。

### action

```

```python
# signup/usecase/action.py
from typing import TypedDict
from ..models import User

class TypeContext(TypedDict):
    """ ユーザ登録結果画面のコンテキストを表現することを責務に持つ """
    user: User


class ResultViewAction:
    """ ユーザ登録結果画面のコンテキストを組み立てることを責務に持つ """

    def __call__(self, user_id: int) -> TypeContext:
        """
        ユーザ情報をコンテキストとして組み立て
        :param user_id 表示対象ユーザID
        :return ユーザ情報を含むコンテキスト
        """
        user = User.objects.get(id=user_id)

        return {
            'user': user
        }
```

### view

```python
# signup/views.py
def result(request: HttpRequest, user_id: int) -> HttpResponse:
    """
    ユーザ登録結果画面
    :param request: HTTPリクエスト
    :param user_id: 表示対象ユーザの識別子
    :return: ユーザ登録結果画面を表現するHTTPレスポンス
    """
    return render(request, 'result.html', context=ResultViewAction()(user_id))
```

### URLconf

```python
from django.urls import path

from .views import index, save, result

app_name = 'ユーザ登録'

urlpatterns = [
    path('', index, name='トップ'),
    path('save', save, name='登録'),

    path('result/<int:user_id>', result, name='登録結果'),
]
```


### ユーザ情報取得

#### 補足: なぜModelではFieldをインスタンス属性ではなくクラス属性で定義したのか

クラスに属性を定義するときは、先ほどまで見てきたクラス属性ではなく、インスタンス属性の方が馴染み深いかもしれません。より具体的には、以下のようにユーザ名属性を定義するようなイメージです。

```python
# signup/models.py
from django.db import models


class User(models.Model):
    """ ユーザ情報を表現することを責務に持つ """
    def __init__(self):
        # ユーザ名カラムを表現する属性
        self.username = models.CharField(max_length=255)
```

このように書いた方が分かりやすそうなのに、なぜクラス属性にFieldを定義するのでしょうか。これは、Modelがデータベースのテーブル・カラムを表わしていることに着目してみると見えてくるかもしれません。


### ユーザ情報表示

## まとめ
