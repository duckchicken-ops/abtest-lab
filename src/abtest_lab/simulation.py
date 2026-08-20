import numpy as np
 
from .testing import ztest_p
 
 
def multi_test_sim(n_segments, n_per_group=1000, p_base=0.12,
                   n_sims=1000, seed=42):
    """세그먼트를 여러 개 볼 때 위양성률이 얼마나 오르는지 측정한다.
 
    두 그룹의 진짜 전환율을 동일하게 두고, 세그먼트 수만 늘려가며
    "하나라도 유의하게 나오는" 실험의 비율을 센다. 모든 세그먼트에
    실제 차이가 없으므로 여기서 나온 값은 전부 위양성이다.
 
    세그먼트가 1개면 유의수준 0.05에 가까운 값이 나온다. 20개로
    늘리면 3분의 2에 가까워진다. 전체 결과가 유의하지 않을 때
    세그먼트를 쪼개 보다가 "모바일 신규 사용자에서는 효과가 있다"는
    결론에 도달하는 과정이 이 확률을 밟고 있는 것이다.
 
    보정(BH, Bonferroni)으로 대응할 수 있지만, 실무에서는 몇 개를
    봤는지 기록되지 않는 경우가 많아 보정 자체가 불가능하다. 그래서
    실험 전에 볼 세그먼트를 지정해두는 편이 더 확실하다.
 
    각 세그먼트는 서로 독립적인 데이터로 시뮬레이션한다. 같은 실험을
    반복해서 보는 상황(peeking_sim)과 구조가 다르며, 위양성률이
    더 가파르게 오르는 이유이기도 하다.
 
    Args:
        n_segments: 한 실험에서 확인하는 세그먼트 수
        n_per_group: 세그먼트별 그룹당 인원. 기본 1000
        p_base: 두 그룹 공통 전환율. 진짜 차이는 0으로 둔다. 기본 0.12
        n_sims: 반복할 실험 횟수. 기본 1000
        seed: 난수 시드
 
    Returns:
        하나 이상의 세그먼트가 유의하게 나온 실험의 비율
 
    Example:
        >>> round(multi_test_sim(1), 2)    # 유의수준 0.05에 근접
        0.04
        >>> round(multi_test_sim(20), 2)   # 세그먼트 20개
        0.66
    """
    rng = np.random.default_rng(seed=seed)
    results = []
 
    for _ in range(n_sims):
        any_sig = False
 
        for _ in range(n_segments):
            conv_a = rng.binomial(n_per_group, p_base)
            conv_b = rng.binomial(n_per_group, p_base)
 
            z, p = ztest_p(n_per_group, n_per_group, conv_a, conv_b)
            if p < 0.05:
                any_sig = True
 
        results.append(any_sig)
 
    return np.mean(results)
 
 
def peeking_sim(n_peeks, n_per_day=200, p_base=0.12,
                n_sims=1000, seed=42):
    """실험 중간에 결과를 반복 확인할 때 위양성률이 얼마나 오르는지 측정한다.
 
    두 그룹의 진짜 전환율을 동일하게 두고, 하루치 데이터를 누적하며
    매일 검정한다. "한 번이라도 유의해진" 실험의 비율을 센다.
    실제 차이가 없으므로 여기서 나온 값은 전부 위양성이다.
 
    1회만 확인하면 0.05 근처지만, 30일 매일 확인하면 4분의 1을
    넘는다. 실험 대시보드가 있는 조직에서는 누구나 매일 보게 되고,
    유의해진 시점에 실험을 멈추면 이 확률이 그대로 현실이 된다.
 
    다중검정(multi_test_sim)보다 상승 폭이 완만하다. 데이터가
    누적되므로 어제 p값과 오늘 p값이 크게 다르지 않기 때문이다.
    반대로 초반에는 표본이 적어 p값이 크게 출렁이므로, 엿보기가
    가장 위험한 구간은 실험 첫 며칠이다.
 
    대응은 세 가지다. 필요 표본에 도달할 때까지 판단을 미루거나,
    모니터링(버그·SRM 감시)과 판단(승패 결정)을 분리하거나,
    순차검정으로 유의수준을 시점마다 나눠 쓰는 것이다.
 
    Args:
        n_peeks: 중간 확인 횟수(일 단위로 간주)
        n_per_day: 하루에 유입되는 그룹당 인원. 기본 200
        p_base: 두 그룹 공통 전환율. 진짜 차이는 0으로 둔다. 기본 0.12
        n_sims: 반복할 실험 횟수. 기본 1000
        seed: 난수 시드
 
    Returns:
        한 번이라도 유의하게 나온 실험의 비율
 
    Example:
        >>> round(peeking_sim(1), 2)     # 종료 후 1회만 확인
        0.04
        >>> round(peeking_sim(30), 2)    # 30일 매일 확인
        0.26
    """
    rng = np.random.default_rng(seed=seed)
    results = []
 
    for _ in range(n_sims):
        any_sig = False
        cum_a = cum_b = cum_n = 0
 
        for _ in range(n_peeks):
            cum_a += rng.binomial(n_per_day, p_base)
            cum_b += rng.binomial(n_per_day, p_base)
            cum_n += n_per_day
 
            z, p = ztest_p(cum_n, cum_n, cum_a, cum_b)
            if p < 0.05:
                any_sig = True
 
        results.append(any_sig)
 
    return np.mean(results)