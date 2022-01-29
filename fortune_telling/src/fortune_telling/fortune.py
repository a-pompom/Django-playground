import random

FORTUNE_CANDIDATE = ['小吉', '中吉', '大吉']


def tell_fortune() -> str:
    """
    運勢の文字列を生成

    :return: 運勢を表す文字列
    """
    fortune = random.randint(0, len(FORTUNE_CANDIDATE) - 1)
    return FORTUNE_CANDIDATE[fortune]
