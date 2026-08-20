from abtest_lab.diagnostics import check_srm


def test_perfect_balance():
    assert check_srm([500, 500])["p_value"] == 1.0


def test_srm_more_sensitive_with_larger_n():
    """같은 48:52라도 표본이 크면 SRM으로 판정된다."""
    assert check_srm([480, 520])["srm"] == False
    assert check_srm([4800, 5200])["srm"] == True


def test_custom_ratio():
    """의도한 90:10 배분은 정상으로 판정한다."""
    assert check_srm([900, 100], [0.9, 0.1])["srm"] == False