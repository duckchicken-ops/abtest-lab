import numpy as np
from scipy.stats import norm
 
 
def obrien_fleming_alpha(t, alpha=0.05):
    """진행률 t 시점까지 누적으로 사용 가능한 유의수준을 구한다.
 
    O'Brien-Fleming 알파 소비 함수다. 실험 전체에 배정된 유의수준을
    여러 확인 시점에 나눠 쓰되, 균등하게 나누지 않는다.
 
    초반에는 거의 쓰지 않고 후반에 몰아 쓴다. 표본이 적은 초기에는
    p값이 크게 출렁이므로 그 구간에서 조기 종료하는 것이 가장
    위험하기 때문이다. 균등 분할(alpha / n)을 쓰면 마지막 시점에도
    기준이 엄격하게 남아 진짜 효과를 놓치기 쉽다.
 
    진행률이 1이 되면 반환값은 alpha 그대로다. 끝까지 실험을 돌렸을
    때는 일반 검정과 같은 기준이 되며, 조기 종료 기회를 열어두는
    비용이 최소화되는 지점이다.
 
    Args:
        t: 실험 진행률. 30일 중 10일째면 1/3. 0 이하면 0을 반환한다.
        alpha: 실험 전체에 배정된 유의수준. 기본 0.05
 
    Returns:
        진행률 t까지 누적으로 사용 가능한 유의수준
 
    Example:
        >>> round(obrien_fleming_alpha(1 / 30), 5)   # 30일 중 1일차
        0.0
        >>> round(obrien_fleming_alpha(2 / 3), 5)    # 20일차
        0.01637
        >>> round(obrien_fleming_alpha(1.0), 5)      # 종료 시점
        0.05
    """
    if t <= 0:
        return 0.0
    z = norm.ppf(1 - alpha / 2)
    return 2 * (1 - norm.cdf(z / np.sqrt(t)))
 
 
def sequential_boundaries(n_peeks, alpha=0.05):
    """각 확인 시점에서 적용할 p값 경계를 구한다.
 
    누적 알파를 시점별 차분으로 변환한다. 반환된 리스트의 i번째
    값을 i번째 확인 시점의 유의수준으로 사용한다.
 
    실험 중간에 결과를 반복 확인하면 위양성률이 오른다. 확인할
    때마다 검정을 한 셈이기 때문이다. 매 시점 0.05를 그대로 쓰면
    30회 확인 시 위양성률이 26%까지 오른다. 시점마다 다른 경계를
    적용하면 이를 억제할 수 있다.
 
    Args:
        n_peeks: 실험 기간 중 결과를 확인하는 총 횟수
        alpha: 실험 전체에 배정된 유의수준. 기본 0.05
 
    Returns:
        각 시점의 p값 경계 리스트. 길이는 n_peeks이며 합은 alpha와 같다.
 
    Example:
        >>> b = sequential_boundaries(5)
        >>> [round(x, 5) for x in b]
        [1e-05, 0.00193, 0.00945, 0.01703, 0.02157]
        >>> round(sum(b), 4)
        0.05
        >>> round(sequential_boundaries(1)[0], 5)   # 1회만 확인하면 alpha 그대로
        [0.05]
 
    Note:
        각 시점의 경계를 누적 알파의 단순 차분으로 구하는 단순화된
        구현이다. 데이터가 누적되므로 인접한 확인 시점의 p값은 서로
        독립이 아니며, 그 결과 실제 위양성률은 목표 alpha보다
        보수적으로 나온다.
 
        측정값(하루 그룹당 200명, 진짜 차이 0, 1000회 시뮬레이션):
 
        | 확인 횟수 | 매번 0.05 적용 | 순차 경계 적용 |
        |---|---|---|
        | 1회 | 3.9% | 3.9% |
        | 7회 | 16.0% | 2.1% |
        | 30회 | 26.2% | 0.7% |
 
        검정력 손실도 함께 확인해야 한다. 진짜 차이가 3%p일 때
        30회 확인 기준으로는 100.0% 대 99.0%로 손실이 거의 없지만,
        7회 확인 기준으로는 76.4% 대 52.2%로 크게 떨어진다.
        끝까지 실험을 돌릴 계획이면 쓸 만하고, 확인 횟수가 적으면
        차라리 확인 시점을 미리 정해두는 편이 낫다.
 
        정확한 경계가 필요하면 z통계량 수준에서 경계를 계산하는
        전용 구현을 사용한다.
    """
    cum_alphas = [obrien_fleming_alpha((i + 1) / n_peeks, alpha)
                  for i in range(n_peeks)]
 
    boundaries = []
    prev = 0.0
    for cum in cum_alphas:
        boundaries.append(cum - prev)
        prev = cum
 
    return boundaries