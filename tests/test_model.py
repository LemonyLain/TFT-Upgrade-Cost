"""Checks that the model reproduces the numbers in the paper."""
import numpy as np

from tftcost import expected_gold, feasible, simulate_gold

INF = float("inf")


def close(a, b, tol=0.05):
    return (a == INF and b == INF) or abs(a - b) <= tol


def test_three_cost_level7_two_star():
    for c, want in enumerate([42.16, 50.22, 63.85, 91.98]):
        assert close(expected_gold(7, 3, 2, c), want)


def test_three_cost_level7_three_star():
    for c, want in enumerate([152.96, 196.33, 298.79, INF]):
        assert close(expected_gold(7, 3, 3, c), want)


def test_other_tiers():
    assert close(expected_gold(5, 1, 3, 3), 216.67)
    assert close(expected_gold(6, 2, 3, 3), 381.97)
    assert close(expected_gold(8, 4, 3, 0), 261.03)
    assert close(expected_gold(10, 5, 3, 0), 337.00)
    assert close(expected_gold(9, 5, 2, 3), 255.79)


def test_infeasible_rule():
    assert not feasible(4, 3, 1)        # 10 - 2.5 < 9
    assert not feasible(5, 3, 1)        # 9 - 1.86 < 9
    assert not feasible(4, 2, 3)        # 10 - 7.5 < 3
    assert feasible(3, 3, 2) and not feasible(3, 3, 3)


def test_cost_rises_with_competitors():
    costs = [expected_gold(7, 3, 2, c) for c in range(4)]
    assert costs == sorted(costs)


def test_simulation_matches_exact():
    g = simulate_gold(7, 3, 2, 2, n=20000, seed=0)
    se = g.std() / np.sqrt(len(g))
    assert abs(g.mean() - expected_gold(7, 3, 2, 2)) < 4 * se
