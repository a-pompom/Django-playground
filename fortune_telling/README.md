おみくじをつくりたい

View, テンプレートを関連付けたい
更に、urlテンプレートタグで逆引きによる画面遷移を実現させたい
公式ドキュメントを読み込みたい
https://docs.djangoproject.com/en/4.0/topics/http/urls

```bash
$ django-admin startproject config .
$ django-admin startapp fortune_telling
```

```bash
$ tree
.
├── README.md
├── __init__.py
├── config
│         ├── __init__.py
│         ├── asgi.py
│         ├── settings.py
│         ├── urls.py
│         └── wsgi.py
├── fortune_telling
│         ├── __init__.py
│         ├── admin.py
│         ├── apps.py
│         ├── migrations
│         │    └── __init__.py
│         ├── models.py
│         ├── tests.py
│         └── views.py
└── manage.py
```

※ Django3.1からsettings.pyのディレクトリの記述がosからpathlibへ変更された
https://docs.djangoproject.com/en/4.0/releases/3.1/#miscellaneous

# 概要

## ゴール

## 用語整理

* テンプレート
* コンテキスト
* 逆引き

## つくりたいもの

## 前準備-復習

### プロジェクトをつくる

### appをつくる

## トップ画面

### テンプレート

#### 置き場所

#### HTML

### view

### URLconf


## おみくじ結果画面

### テンプレート

### view

### おみくじ結果

### URLconf

## 動作確認

### リンクで繋げる

### 画面表示

## まとめ