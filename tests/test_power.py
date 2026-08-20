from abtest_lab.power import sample_size, mde_from_n


def test_sample_size_known_value():
    assert sample_size(0.12, 0.03) == 2036


def test_smaller_mde_needs_more_samples():
    """MDE가 작아지면 필요 표본이 늘어난다."""
    assert sample_size(0.12, 0.01) > sample_size(0.12, 0.05)


def test_larger_n_detects_smaller_effect():
    """표본이 크면 더 작은 차이를 감지할 수 있다."""
    assert mde_from_n(0.12, 10000) < mde_from_n(0.12, 400)