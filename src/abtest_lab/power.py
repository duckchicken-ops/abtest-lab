import math

import numpy as np
from scipy.stats import norm


def sample_size(p_base, mde, alpha=0.05, power=0.8):
    """지정한 크기의 차이를 감지하는 데 필요한 그룹당 표본 수를 구한다.
 
    실험을 시작하기 전에 계산한다. 필요 표본에 도달하기 전까지는
    중간 결과로 승패를 판단하지 않는 것이 원칙이다.
 
    감지하려는 차이와 필요 표본은 제곱 관계에 있다. MDE를 절반으로
    줄이면 표본은 약 4배가 필요하다. 작은 효과를 검증하는 일이
    비싼 이유이며, 기대 효과 크기를 먼저 합의해야 하는 이유이기도 하다.
 
    검정력 0.8은 진짜 차이가 있어도 5번 중 1번은 놓친다는 뜻이다.
    관례적으로 쓰이지만 관대한 기준이므로, 중요한 의사결정에는
    0.9를 쓰기도 한다.
 
    Args:
        p_base: 현재 전환율(기준선). 예) 0.12
        mde: 감지하려는 최소 차이(%p 단위의 소수). 예) 0.03
        alpha: 1종 오류 허용치. 기본 0.05
        power: 검정력. 진짜 차이를 잡아낼 확률. 기본 0.8
 
    Returns:
        그룹당 필요한 인원(올림한 정수)
 
    Example:
        >>> sample_size(0.12, 0.03)
        2036
        >>> sample_size(0.12, 0.015)   # MDE 절반 -> 표본 약 4배
        7761
    """

    z_alpha = norm.ppf(1 - alpha / 2)                               # z_alpha, power = 임계값

    z_power = norm.ppf(power)

    p1 = p_base                                                     # p1, p2 = 비교 대상 비율
    p2 = p_base + mde

    p_bar = (p1 + p2) / 2
    numerator = (z_alpha * np.sqrt(2 * p_bar * (1 - p_bar))         #최소 표본수 공식
                 + z_power * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    n = numerator / (mde ** 2)

    return math.ceil(n)   

def mde_from_n(p_base, n_per_group, alpha=0.05, power=0.8):
    """주어진 표본으로 감지할 수 있는 최소 차이를 구한다.
 
    트래픽이 정해져 있을 때 사용한다. 실무에서는 표본을 늘리는 쪽보다
    "이번 주 트래픽으로 무엇을 볼 수 있는가"를 묻는 경우가 더 많다.
 
    관측된 차이가 여기서 나온 값보다 작다면, 그 실험은 애초에
    결론이 나올 수 없는 설계였다는 뜻이다. 표본을 더 모으거나
    실험을 중단하는 판단의 근거가 된다.
 
    공식을 역산하지 않고 MDE를 0.1%p씩 키우며 조건을 만족하는
    첫 값을 찾는다. 정밀도는 0.001로 제한되지만 실무에는 충분하다.
 
    Args:
        p_base: 현재 전환율(기준선)
        n_per_group: 그룹당 확보 가능한 인원
        alpha: 1종 오류 허용치. 기본 0.05
        power: 검정력. 기본 0.8
 
    Returns:
        감지 가능한 최소 차이(소수). 20%p까지 키워도 표본이
        부족하면 None
 
    Example:
        >>> round(mde_from_n(0.12, 400), 3)    # 5%p 차이는 감지 불가
        0.072
        >>> round(mde_from_n(0.12, 10000), 3)
        0.014
    """

    for mde in np.arange(0.001, 0.20, 0.001):
        if sample_size(p_base, mde, alpha, power) <= n_per_group:
            return mde
    return None