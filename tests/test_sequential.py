from abtest_lab.sequential import obrien_fleming_alpha, sequential_boundaries


def test_boundaries_sum_to_alpha():
    """경계값의 합이 alpha와 같다."""
    b = sequential_boundaries(10)
    assert abs(sum(b) - 0.05) < 1e-9


def test_early_boundary_is_strict():
    """초반 경계가 후반보다 엄격하다."""
    b = sequential_boundaries(10)
    for i in range(len(b) - 1):
        assert b[i] < b[i + 1]


def test_single_peek_equals_alpha():
    """1회만 확인하면 기준이 alpha 그대로다."""
    b = sequential_boundaries(1)
    assert len(b) == 1
    assert abs(b[0] - 0.05) < 1e-9