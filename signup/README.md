# 概要

Djangoでユーザ登録アプリをつくってみます。

## ゴール

Djangoが用意しているModelの概要を理解し、データベース操作へ入門してみることを目指します。
※ 以降ではデータベースが指すものをリレーショナルデータベースに限定します。

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


## データベース整備-前準備

データベースを扱うアプリケーションでは、どのようなデータを保存・参照するのかあらかじめ決めておくことが重要です。ユーザ登録機能では、ユーザ情報として何を登録して何を表示するのか決めておけば、迷うことなく開発が進められそうです。
よって、まずはユーザ情報を保存するデータベースのテーブルをつくることから始めます。

最初に、データベースを組み立てるためのDjangoの機能にどのようなものがあるのか、概略を見ていきます。概念を押さえたあとは、手を動かしながらユーザ登録機能を実現するのに必要なものを用意していきます。

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

DjangoのModelとMVCモデルのM(Model)は同じ単語で表現されています。DjangoのModelが意味するところをより深く理解するためにも、MVCのModelが指すものとの関係を整理してみます。

[参考](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller)

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

話が難しくなってしまいましたが、Modelという抽象的な単語をさまざまな側面で比較してみることで、DjangoにおけるModelが何を指しているのか少しでも見えてくれば幸いです。


### Migrations

DjangoのModelは、アプリケーションで扱うデータを表現したものであることが分かりました。それならば、Modelからデータベースの対応するテーブルをつくってくれるような機能が欲しくなるところです。ModelとデータベースをDjangoがマッピングしてくれれば、まさに定義通りModelがアプリケーションのデータを表現していると言えるはずです。
そこで、DjangoではModelの情報をデータベースへ反映する`migration`という機能を用意してくれています。

[参考](https://docs.djangoproject.com/en/4.1/topics/migrations/)

migrationそのものの概要を復習しておきたい場合は、[参考リンク](https://martinfowler.com/articles/evodb.html#AllDatabaseChangesAreMigrations)を見てみてください。

Djangoのmigration機能は、2つの管理コマンドによって実現されます。
Modelをデータベースへ反映するためのファイル(migrationファイル)を`makemigrations`コマンドでつくり、`migrate`コマンドでデータベースへ反映します。

#### 補足: なぜ`makemigrations`コマンドが必要なのか

Modelをデータベースへ反映させるのであれば、`migrate`コマンド1つで十分なように思えます。なぜわざわざ`makemigrations`コマンドでファイルをつくるのでしょうか。
これは、データベースへの変更内容をファイルで表現することで、データベース操作をバージョン管理するためです。
`makemigrations`コマンドでつくられたファイルをバージョン管理しておくことで、アプリケーションのデータベースを任意の状態・任意の環境で組み立てられるようになります。
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

#### `DATABASES`

設定値は`DATABASES`に辞書形式で書かれています。辞書の各キーが何を表すのか、簡単に見ておきます。
[参考](https://docs.djangoproject.com/en/4.1/ref/settings/#databases)

#### `default`

`default`キーは、複数のデータベースを切り替えない限りはあまり意識することはないかと思います。
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

ModelはPythonのクラスでデータベースのテーブルを表現しています。ですので、ユーザ情報としてユーザ名を属性に持つクラスをModelとしてつくってみることにします。

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

続いて、データベースのテーブルのカラムをクラス属性で表現しています。

[参考](https://docs.djangoproject.com/en/4.1/topics/db/models/)

Modelのクラス属性には何を書いてもいいわけではなく、`Field`と呼ばれるものを定義します。

[参考](https://docs.djangoproject.com/en/4.1/topics/db/models/#fields)

Fieldはテーブルのカラムを表現しており、型や制約の情報を持ちます。
Djangoでは型に応じてさまざまなFieldを提供しており、単純な文字列を表現するカラムでは、`CharField`が用意されています。

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

※ 書式上は`django-admin`で指定されていますが、`python manage.py`でも同じように書くことができます。
[参考](https://docs.djangoproject.com/en/4.1/ref/django-admin/)

```bash
$ python manage.py makemigrations signup
Migrations for 'signup':
  signup/migrations/0001_initial.py
    - Create model User
```

`signup/migrations`ディレクトリへマイグレーションファイルとして、`0001_initial.py`がつくられたようです。
Djangoがよしなにやってくれるところではありますが、雰囲気を掴むために中身もざっと見ておきましょう。

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

Modelのように、Pythonのクラス形式でmigrationを表現しているようです。クラス属性などから、新しくModelをつくることが読み取れます。
ただ、データベースのカラムを表す`fields`と呼ばれる箇所を見てみると、idなる見慣れないものが加わっています。実はDjangoでは、明示的に主キーを定義しなかった場合、連番形式のカラムidを主キーとして補ってくれます。より具体的なところは、発行されるSQLを見ることで雰囲気が掴めるはずです。

[参考](https://docs.djangoproject.com/en/4.1/topics/db/models/#automatic-primary-key-fields)

#### `sqlmigrate`コマンド

あとは`migrate`コマンドでModelをデータベースへ反映してもらうだけです。ですがこれだけでは裏側のSQLがすべて隠れてしまっているので、何が起こっているのか見えづらいです。
そこで`sqlmigrate`なるコマンドから、`migrate`コマンドが実行してくれるSQLを覗いておきましょう。

[参考](https://docs.djangoproject.com/en/4.1/ref/django-admin/#sqlmigrate)

> 書式: `django-admin sqlmigrate app_label migration_name`

`app_label`引数にはappの名前として`signup`を・`migration_name`には拡張子を除いたマイグレーションファイル名を指定します。

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

先ほどつくったユーザ登録app以外にもたくさんの内容が出力されました。これは一体何を表しているのでしょうか。
`migrate`コマンドで引数を指定しない場合、`settings.py`の`INSTALLED_APPS`に書かれたすべてのappのマイグレーションファイルがデータベースへ反映されます。
ひとまずは、ここではDjangoが用意してくれていたマイグレーションファイルもデータベースへ反映したんだな、ということだけ押さえておきましょう。

データベースを見てみると、確かに`migrate`コマンドによりデータベースへテーブルがつくられていました。

![image](https://user-images.githubusercontent.com/43694794/188301821-15673ac4-9209-4c47-842e-f8be1ac885f6.png)

また、本命のユーザ情報を表現するテーブル`signup_user`も期待通りの形にできあがっていました。

![image](https://user-images.githubusercontent.com/43694794/188301831-d853e943-5893-4d2b-9392-58222f097f91.png)

---

ようやく最初にゴールとして掲げていた、ユーザ情報を表現するデータベースのテーブルをつくるところまでたどり着けました。
たくさんの用語やコマンドが出てきましたが、一度にすべてを理解しようと思うとしんどくなってしまいます。データベースはこれからたくさん触っていくので、少しずつ身につけていきましょう。


## ユーザ登録画面

土台が出来上がったので、いよいよユーザ登録機能をつくっていきます。まずは入り口となるユーザ登録画面から始めます。
テンプレートの復習がてら、画面を表示するところまで通していきましょう。

### テンプレートの設定

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

```bash
$ ls
__init__.py config      db.sqlite3  manage.py   signup
# appやconfigディレクトリと同じ階層にtemplatesディレクトリを作成
$ mkdir templates
```



### ユーザ登録処理

### PRGパターン

## ユーザ登録結果画面

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
$ python manage.py migrate
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, signup
Running migrations:
  Applying signup.0001_initial... OK
```