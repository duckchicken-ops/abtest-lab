import numpy as np
 
 
def apply_cuped(post, pre):
    """CUPED로 지표의 분산을 줄인다.
 
    실험 전 데이터(공변량)를 이용해 개인차에서 오는 노이즈를 걷어낸다.
    실험 중 매출이 큰 사용자는 실험 전에도 컸을 가능성이 높은데,
    그 부분은 처치 효과가 아니라 원래의 성향이다. 이를 제거하면
    남는 변동이 처치 효과에 가까워진다.
 
    같은 표본으로 더 작은 차이를 감지할 수 있게 된다. 표준편차가
    절반이 되면 표본의 4분의 1로 같은 정밀도를 얻는 셈이다.
    표본을 늘리기 어려운 상황에서 쓸 수 있는 우회로다.
 
    공변량은 반드시 실험 시작 전 기간의 값이어야 한다. 실험 중
    데이터를 쓰면 처치 효과 자체를 빼버리게 되며, 이것이 가장 흔한
    오용이다.
 
    theta는 공변량과 지표의 연관 강도에 따라 자동으로 정해진다.
    둘이 무관하면 0에 가까워져 보정이 거의 일어나지 않으므로,
    쓸모없는 공변량을 넣어도 손해는 없다. 다만 효과도 없다.
 
    보정 후에도 전체 평균은 유지된다. 줄이는 것은 편차이지 수준이
    아니므로, "평균 매출 12,000원" 같은 해석이 그대로 유지된다.
 
    Args:
        post: 실험 기간의 지표값 배열
        pre: 실험 전 기간의 같은 지표값 배열. post와 길이가 같아야 하며
            실험의 영향을 받지 않은 값이어야 한다.
 
    Returns:
        (post_adj, theta)
            post_adj: 분산이 줄어든 지표값 배열
            theta: 보정 계수. 0에 가까우면 공변량이 도움이 되지 않았다는 뜻
 
    Example:
        >>> import numpy as np
        >>> rng = np.random.default_rng(seed=42)
        >>> pre = rng.normal(100, 20, size=1000)
        >>> post = pre * 0.8 + rng.normal(0, 10, size=1000)
        >>> post_adj, theta = apply_cuped(post, pre)
        >>> post_adj.std() < post.std()
        True
 
    Note:
        실제 서비스에서는 20~50% 분산 감소가 일반적이다. 공변량과
        지표의 상관이 강할수록 효과가 크므로, 같은 지표의 직전 기간
        값을 쓰는 것이 보통 가장 잘 작동한다.
    """
    theta = np.cov(post, pre)[0, 1] / np.var(pre)
    post_adj = post - theta * (pre - pre.mean())
    return post_adj, theta