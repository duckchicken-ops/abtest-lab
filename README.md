# abtest-lab

![tests](https://github.com/duckchicken-ops/abtest-lab/actions/workflows/test.yml/badge.svg)

A/B 테스트가 조용히 틀리는 지점을 시뮬레이션으로 검증하는 도구.

## 핵심 발견

| 상황               | 위양성률 |
| ------------------ | -------- |
| 정상 (1회 검정)    | 5%       |
| 세그먼트 20개 확인 | **66%**  |
| 30일 매일 확인     | **26%**  |

세 경우 모두 두 그룹에 실제 차이 없음.
각 수치는 1,000회 시뮬레이션으로 측정했으며, `notebooks/`에서 재현 가능.

순차검정을 적용하면 30일 매일 확인해도 위양성률이 0.7%로 유지되며,
검정력 손실은 1%p에 그친다(`02_sequential`).

대응 기법도 함께 다룬다. CUPED로 분산을 절반으로 줄여 같은 데이터에서
p값이 0.0713 → 0.0039로 개선되는 사례를 `05_cuped`에서 확인할 수 있다.

## 왜 만들었나

A/B 테스트 결과를 판정하는 과정을 학습하면서, 두 그룹에 진짜 차이가 0인 데이터에서
5%p차이가 관측되는 경우가 반복해서 발생, 오류도 경고도 없이 그럴듯한 숫자가 나오기 때문으로
코드를 아무리 검토해도 발견이 어려움.
이런 실패는 세가지 경로로 발생.
세그먼트를 여러개 확인하거나, 실험 중간에 반복해서 들여다보거나, 배정 비율이 어긋난 경우.
각각이 얼마나 위험한지 수치로 확인하기 위해 시뮬레이션으로 정량화.

## 노트북

|                                                            | 내용                                    |
| ---------------------------------------------------------- | --------------------------------------- |
| [01_peeking](notebooks/01_peeking.ipynb)                   | 실험 중간 확인이 위양성률에 미치는 영향 |
| [02_sequential](notebooks/02_sequential.ipynb)             | 알파 소비 함수로 엿보기 문제 억제       |
| [03_multiple_testing](notebooks/03_multiple_testing.ipynb) | 세그먼트를 여러 개 볼 때의 위험과 보정  |
| [04_srm](notebooks/04_srm.ipynb)                           | 배정 비율 불일치 탐지와 대응            |
| [05_cuped](notebooks/05_cuped.ipynb)                       | 실험 전 데이터로 분산을 줄여 표본 절약  |

## 문서

노트북이 함정의 존재를 보인다면, 아래 문서는 그것을 피하는 절차를 담는다.

- [실험 설계 템플릿](docs/experiment_design_template.md) — 실험 시작 전 작성하는 체크리스트
- [작성 예시](docs/example_checkout_button.md) — 템플릿을 채운 가상 사례

## 설치

```bash
git clone https://github.com/duckchicken-ops/abtest-lab.git
cd abtest-lab
uv sync
```

## 사용법

### 실험 전 — 필요 표본 계산

```python
from abtest_lab.power import sample_size

sample_size(p_base=0.12, mde=0.03)
# 2036 (그룹당)
```

### 실험 후 — 판정

```python
from abtest_lab.testing import ztest_p, ztest_ci

ztest_p(491, 509, 62, 62)
# (0.214, 0.830)

ztest_ci(491, 509, 62, 62)
# (-0.036, 0.045)  구간이 0을 포함 → 판단 불가
```

### 신뢰도 점검

```python
from abtest_lab.diagnostics import check_srm

check_srm([4800, 5200])
# {'p_value': 6.3e-05, 'srm': True, ...}
```

### 분산 감소

```python
from abtest_lab.variance import apply_cuped

post_adj, theta = apply_cuped(post, pre)
# 표준편차 6405.7 → 3021.1 (theta=0.807)
```

### 중간 확인이 필요할 때

```python
from abtest_lab.sequential import sequential_boundaries

sequential_boundaries(5)
# [1e-05, 0.00193, 0.00945, 0.01703, 0.02157]
# 각 확인 시점에 적용할 p값 기준. 합은 0.05
```

## 구조

```
abtest-lab/
├── src/abtest_lab/
│   ├── testing.py       # 가설검정 (z검정, 신뢰구간, 순열검정)
│   ├── power.py         # 표본수·MDE 계산
│   ├── diagnostics.py   # SRM 탐지
│   ├── variance.py      # CUPED 분산 감소
│   ├── simulation.py    # 위양성률 시뮬레이션
│   ├── sequential.py    # 순차검정 (알파 소비 함수)
├── tests/               # pytest 17개
├── notebooks/           # 시연 노트북 4개
└── pyproject.toml
```

## 테스트

```bash
uv run pytest
```
