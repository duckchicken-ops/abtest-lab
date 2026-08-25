# abtest-lab

![tests](https://github.com/duckchicken-ops/abtest-lab/actions/workflows/test.yml/badge.svg)

[한국어](README.md)

A tool for validating easy-to-overlook statistical errors in A/B testing through simulations.

## Key findings

| Situation                  | False positive rate |
| -------------------------- | ------------------- |
| Baseline (single test)     | 5%                  |
| Checking 20 segments       | **66%**             |
| Checking daily for 30 days | **26%**             |

In all three cases the two groups have no real difference.
Each figure comes from 1,000 simulations and is reproducible
in `notebooks/`.

Sequential testing keeps the false positive rate at 0.7% even
with daily checks over 30 days, at a cost of 1 percentage point in power
(`02_sequential`). CUPED cuts the standard deviation roughly in
half, moving p from 0.0713 to 0.0039 on identical data
(`05_cuped`).

## Why I built this

While learning to evaluate A/B test results, I kept running into cases
where data with **zero actual difference** between
the two groups showed a 5 percentage point gap.
No error, no warning — just plausible-looking numbers that code review cannot catch.

Three paths lead to this: checking many segments,
looking at results repeatedly during the experiment, and mismatched assignment ratios.

I quantified the risks of each scenario through simulations and documented practical strategies in the experiment design guidelines to avoid them.

## Notebooks

|                                                            | Topic                                             |
| ---------------------------------------------------------- | ------------------------------------------------- |
| [01_peeking](notebooks/01_peeking.ipynb)                   | How mid-experiment checks inflate false positives |
| [02_sequential](notebooks/02_sequential.ipynb)             | Alpha spending to control the peeking problem     |
| [03_multiple_testing](notebooks/03_multiple_testing.ipynb) | Risks and corrections when checking many segments |
| [04_srm](notebooks/04_srm.ipynb)                           | Detecting and responding to sample ratio mismatch |
| [05_cuped](notebooks/05_cuped.ipynb)                       | Reducing variance with pre-experiment data        |

## Documentation

The notebooks show that these traps exist. The documents below describe
how to avoid them.

- [Experiment Design Template](docs/experiment_design_template.md) — a checklist to fill in before starting an experiment
- [Worked Example](docs/example_checkout_button.md) — the template filled in for a hypothetical experiment

## Installation

```bash
git clone https://github.com/duckchicken-ops/abtest-lab.git
cd abtest-lab
uv sync
```

## Usage

### Before the experiment — sample size

```python
from abtest_lab.power import sample_size

sample_size(p_base=0.12, mde=0.03)
# 2036 per group
```

### After the experiment — evaluation

```python
from abtest_lab.testing import ztest_p, ztest_ci

ztest_p(491, 509, 62, 62)
# (0.214, 0.830)

ztest_ci(491, 509, 62, 62)
# (-0.036, 0.045)  interval contains 0 -> inconclusive
```

### Sanity check (SRM)

```python
from abtest_lab.diagnostics import check_srm

check_srm([4800, 5200])
# {'p_value': 6.3e-05, 'srm': True, ...}
```

### Variance reduction

```python
from abtest_lab.variance import apply_cuped

post_adj, theta = apply_cuped(post, pre)
# standard deviation 6405.7 → 3021.1 (theta=0.807)
```

### When mid-experiment checks are needed

```python
from abtest_lab.sequential import sequential_boundaries

sequential_boundaries(5)
# [1e-05, 0.00193, 0.00945, 0.01703, 0.02157]
# p-value thresholds for each check; they sum to 0.05
```

## Structure

```
abtest-lab/
├── src/abtest_lab/
│   ├── testing.py       # hypothesis testing (z-test, confidence interval, permutation test)
│   ├── power.py         # sample size and MDE calculation
│   ├── diagnostics.py   # SRM detection
│   ├── variance.py      # CUPED variance reduction
│   ├── simulation.py    # false positive rate simulation
│   └── sequential.py    # sequential testing (alpha spending function)
├── tests/               # 17 pytest cases
├── notebooks/           # 5 demonstration notebooks
├── docs/                # experiment design template and example
└── pyproject.toml
```

## Tests

```bash
uv run pytest
```
