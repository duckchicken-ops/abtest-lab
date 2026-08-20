# abtest-lab

A/B 테스트가 조용히 틀리는 지점을 시뮬레이션으로 검증하는 도구.

## 핵심 발견

| 상황               | 위양성률 |
| ------------------ | -------- |
| 정상 (1회 검정)    | 5%       |
| 세그먼트 20개 확인 | **66%**  |
| 30일 매일 확인     | **26%**  |

세 경우 모두 두 그룹에 실제 차이 없음.
각 수치는 1,000회 시뮬레이션으로 측정했으며, `notebooks/`에서 재현 가능.

## 왜 만들었나

A/B 테스트 결과를 판정하는 과정을 학습하면서, 두 그룹에 진짜 차이가 0인 데이터에서
5%p차이가 관측되는 경우가 반복해서 발생, 오류도 경고도 없이 그럴듯한 숫자가 나오기 때문으로
코드를 아무리 검토해도 발견이 어려움.
이런 실패는 세가지 경로로 발생.
세그먼트를 여러개 확인하거나, 실험 중간에 반복해서 들여다보거나, 배정 비율이 어긋난 경우.
각각이 얼마나 위험한지 수치로 확인하기 위해 시뮬레이션으로 정량화.

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

## 구조

```
abtest-lab/
├── src/abtest_lab/
│   ├── testing.py       # 가설검정 (z검정, 신뢰구간, 순열검정)
│   ├── power.py         # 표본수·MDE 계산
│   ├── diagnostics.py   # SRM 탐지
│   └── simulation.py    # 위양성률 시뮬레이션
├── tests/               # pytest 11개
├── notebooks/
│   └── 01_peeking.ipynb # 엿보기 문제 시연
└── pyproject.toml
```

## 테스트

```bash
uv run pytest
```
