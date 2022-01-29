from fortune_telling.fortune import tell_fortune, FORTUNE_CANDIDATE


# 運勢は候補の中から選ばれるか
def test_fortune_in_candidate():
    # GIVEN
    sut = tell_fortune
    # WHEN
    actual = sut()
    # THEN
    assert actual in FORTUNE_CANDIDATE
