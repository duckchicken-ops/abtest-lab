from abtest_lab.testing import ztest_p, ztest_ci, permutation_p


def test_ztest_p_known_value():
    z, p = ztest_p(491, 509, 62, 62)
    assert round(p, 4) == 0.8304


def test_ztest_ci_known_value():
    lo, hi = ztest_ci(491, 509, 62, 62)
    assert round(lo, 4) == -0.0364
    assert round(hi, 4) == 0.0453


def test_identical_groups_give_high_p():
    """두 그룹이 완전히 같으면 p값이 1에 가깝다."""
    z, p = ztest_p(1000, 1000, 120, 120)
    assert p > 0.9


def test_permutation_matches_ztest():
    """순열검정과 z검정이 비슷한 답을 낸다."""
    p_perm = permutation_p(491, 509, 62, 62, n_trials=5000)
    z, p_z = ztest_p(491, 509, 62, 62)
    assert abs(p_perm - p_z) < 0.05

def test_ztest_p_zero_conversions():
    """양쪽 전환자가 0명이면 차이 없음으로 처리한다."""
    z, p = ztest_p(100, 100, 0, 0)
    assert z == 0.0
    assert p == 1.0