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
