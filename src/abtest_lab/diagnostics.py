from scipy.stats import chisquare

def check_srm(counts, expected_ratio=None, alpha=0.001):
    """실험군 배정 비율이 의도와 어긋났는지(SRM) 검정한다.
 
    SRM(Sample Ratio Mismatch)이 발견되면 실험 결과를 보정하지 않고
    폐기한다. 어떤 사용자가 어떤 이유로 빠졌는지 알 수 없어 보정할
    방법이 없기 때문이다. 사라진 사용자는 무작위가 아니라 특정 브라우저
    사용자나 이탈이 빠른 사용자처럼 한쪽으로 치우친 집단일 가능성이 높다.
 
    그래서 다른 분석보다 먼저 확인한다. SRM을 통과하지 못한 실험의
    전환율 비교는 의미가 없다.
 
    유의수준은 일반 검정보다 엄격한 0.001을 기본으로 쓴다. 실험을
    다수 운영하는 환경에서 0.05를 쓰면 정상 실험의 5%가 경보를 울려
    아무도 경보를 믿지 않게 된다.
 
    표본이 클수록 같은 비율 차이도 SRM으로 판정된다. 트래픽이 큰
    서비스에서 경보가 잦은 것은 도구가 예민해서가 아니라, 작은
    어긋남도 우연으로 설명되지 않기 때문이다.
 
    Args:
        counts: 그룹별 실제 인원 리스트. 예) [491, 509]
        expected_ratio: 의도한 배정 비율. 예) [0.5, 0.5] 또는 [0.9, 0.1].
            None이면 균등 배분으로 간주한다.
        alpha: 경보 기준. 기본 0.001
 
    Returns:
        dict:
            p_value: 카이제곱 검정의 p값
            srm: p값이 alpha 미만이면 True(문제 있음)
            expected: 의도한 비율에 따른 기대 인원
            actual_ratio: 실제 관측된 비율
 
    Example:
        >>> r = check_srm([491, 509])
        >>> r["srm"]
        False
        >>> r = check_srm([4800, 5200])   # 같은 48:52도 표본이 크면 경보
        >>> r["srm"]
        True
        >>> r = check_srm([900, 100], [0.9, 0.1])   # 의도한 90:10
        >>> r["srm"]
        False
 
    Note:
        SRM 발생 시 확인 순서
        1. 배정 로직 - 랜덤 시드, 해시 함수가 균등한가
        2. 분석 쿼리의 필터 조건 - 한쪽만 걸러내고 있지 않은가
        3. 기록 유실 - 한쪽 페이지가 느려 이벤트가 덜 남지 않는가
        4. 리다이렉트 - 한쪽만 페이지 이동이 있어 이탈이 생기지 않는가
    """
    total = sum(counts)
 
    if expected_ratio is None:
        expected_ratio = [1 / len(counts)] * len(counts)
 
    expected = [total * r for r in expected_ratio]
    stat, p = chisquare(f_obs=counts, f_exp=expected)
    actual_ratio = [c / total for c in counts]
 
    return {
        "p_value": p,
        "srm": p < alpha,
        "expected": expected,
        "actual_ratio": [round(r, 4) for r in actual_ratio],
    }