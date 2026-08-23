import numpy as np

from abtest_lab.variance import apply_cuped


def test_cuped_reduces_variance():
    """공변량과 상관이 높으면 분산이 줄어든다."""
    rng = np.random.default_rng(seed=42)
    pre = rng.normal(100, 20, size=1000)
    post = pre * 0.8 + rng.normal(0, 10, size=1000)

    post_adj, theta = apply_cuped(post, pre)

    assert post_adj.std() < post.std()


def test_cuped_preserves_mean():
    """평균은 유지된다."""
    rng = np.random.default_rng(seed=42)
    pre = rng.normal(100, 20, size=1000)
    post = pre * 0.8 + rng.normal(0, 10, size=1000)

    post_adj, theta = apply_cuped(post, pre)

    assert abs(post_adj.mean() - post.mean()) < 1e-9


def test_cuped_no_effect_when_uncorrelated():
    """공변량이 무관하면 거의 변화가 없다."""
    rng = np.random.default_rng(seed=42)
    pre = rng.normal(100, 20, size=1000)
    post = rng.normal(50, 10, size=1000)

    post_adj, theta = apply_cuped(post, pre)

    assert abs(theta) < 0.1
    assert post_adj.std() > post.std() * 0.95