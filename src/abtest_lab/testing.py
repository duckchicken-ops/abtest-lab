import numpy as np
from scipy.stats import norm


def ztest_p(n_a, n_b, conv_a, conv_b):
    """두 비율의 차이에 대한 z검정.

    Args:
        n_a: A그룹 전체 인원
        n_b: B그룹 전체 인원
        conv_a: A그룹 전환자 수
        conv_b: B그룹 전환자 수

    Returns:
        (z, p) — z통계량과 양측 p값,
        양쪽 전환율이 동일하게 0 또는 1이면 표준오차가 0이 되어
        계산이 불가능하다. 이 경우 차이가 없는 것으로 보아 (0.0, 1.0)을 반환한다.
    """

    p_pool = (conv_a + conv_b) / (n_a + n_b)                        #통합 비율
    se = np.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b))       #표준 오차

    if se == 0:
        return 0.0, 1.0

    z = (conv_a / n_a - conv_b / n_b) / se                          #z값
    p = 2 * (1 - norm.cdf(abs(z)))                                  #p값
    return z, p


def ztest_ci(n_a, n_b, conv_a, conv_b, conf=0.95):
    """두 비율 차이의 신뢰구간.

    A그룹 비율에서 B그룹 비율을 뺀 값의 신뢰구간을 구한다.
    구간이 0을 포함하면 어느 쪽이 우세한지 판단할 수 없다.
    구간의 폭은 표본 크기를 반영하므로, 넓으면 데이터가 부족하다는 뜻이다.

    p값 계산과 달리 통합 비율을 쓰지 않는다. "차이가 없다"는 가정을
    하지 않고 관측된 각 그룹의 비율을 그대로 사용한다.

    Args:
        n_a: A그룹 전체 인원
        n_b: B그룹 전체 인원
        conv_a: A그룹 전환자 수
        conv_b: B그룹 전환자 수
        conf: 신뢰수준. 기본 0.95

    Returns:
        (lower, upper) — 차이(A - B)의 신뢰구간 하한과 상한

    Example:
        >>> lo, hi = ztest_ci(491, 509, 62, 62)
        >>> round(lo * 100, 2), round(hi * 100, 2)
        (-3.64, 4.53)
    """

    diff = conv_a / n_a - conv_b / n_b                              #관측된 차이
    p_a = conv_a / n_a
    p_b = conv_b / n_b
    se = np.sqrt(p_a * (1 - p_a) / n_a + p_b * (1 - p_b) / n_b)     #표준오차
    z_crit = norm.ppf(1 - (1 - conf) / 2)                           #임계값
    margin = z_crit * se                                            #구간
    return (diff - margin, diff + margin)


def permutation_p(n_a, n_b, conv_a, conv_b, n_trials=10000, seed=42):
    """순열검정으로 두 비율 차이의 p값을 구한다.

    두 그룹의 성능이 같다면 누가 A이고 B인지는 무의미하다는 점을 이용한다.
    전체 데이터를 한 통에 합친 뒤 무작위로 다시 나누기를 반복해,
    관측된 만큼의 차이가 우연히 나오는 빈도를 센다.

    공식(ztest_p)과 결과가 거의 같지만 느리다. 정규근사가 어려운
    작은 표본이나, 공식 결과를 검증할 때 사용한다.

    Args:
        n_a: A그룹 전체 인원
        n_b: B그룹 전체 인원
        conv_a: A그룹 전환자 수
        conv_b: B그룹 전환자 수
        n_trials: 재배치 반복 횟수. 기본 10000
        seed: 난수 시드. 결과 재현을 위해 고정

    Returns:
        양측 p값

    Example:
        >>> round(permutation_p(491, 509, 62, 62), 2)
        0.83
    """

    rng = np.random.default_rng(seed=seed)          

    n_total = n_a + n_b                              # 차이가 없는 세계 → 한 통에 합침
    n_conv = conv_a + conv_b

    outcomes = np.zeros(n_total)                     
    outcomes[:n_conv] = 1                            # 전환자만 1로 표시

    observed = abs(conv_a / n_a - conv_b / n_b)      # 관측된 차이 (절댓값)

    diffs = []                                       
    for _ in range(n_trials):
        shuffled = rng.permutation(outcomes)
        d = shuffled[:n_a].mean() - shuffled[n_a:].mean()
        diffs.append(d)
    diffs = np.array(diffs)                          # ← D4: 마스크를 쓰려면 배열이어야 함

    return (np.abs(diffs) >= observed).mean()        # ← D4: 계수 패턴, 마스크의 평균 = 비율