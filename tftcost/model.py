"""Upgrade-cost model for Teamfight Tactics Set 18.

The state is the number of copies of one target unit that I own. Each shop
shows 5 slots, and a slot shows the target with probability

    p_s = odds(level, cost) * (T - K - s) / ((T - K - s) + R)

T = copies of the target in the full pool, K = competitors * h (copies held by
competitors), s = copies I own, R = copies of the other champions of that tier
still in the pool. Hits per shop are Binomial(5, p_s). The goal state
(3 copies for a 2-star, 9 for a 3-star) is absorbing, so the expected number of
shops comes from the fundamental matrix (I - Q)^-1.

H (copies per competitor) and BG (background depletion) were estimated from
7,995 final boards of NA Challenger matches; see the paper and notebook 04.
"""
from __future__ import annotations

from math import comb

import numpy as np

SLOTS = 5
REROLL_COST = 2
NEED = {2: 3, 3: 9}                       # copies needed for a 2-star / 3-star

COPIES = {1: 30, 2: 25, 3: 18, 4: 10, 5: 9}      # copies of each champion
CHAMPS = {1: 14, 2: 13, 3: 14, 4: 14, 5: 10}     # champions per cost tier

# Set 18 shop odds in percent: ODDS[level] = [1-cost, 2-cost, 3-cost, 4-cost, 5-cost]
ODDS = {
    1: [100, 0, 0, 0, 0], 2: [100, 0, 0, 0, 0], 3: [75, 25, 0, 0, 0],
    4: [55, 30, 15, 0, 0], 5: [45, 33, 20, 2, 0], 6: [30, 40, 25, 5, 0],
    7: [16, 30, 43, 10, 1], 8: [15, 20, 32, 30, 3], 9: [10, 17, 25, 33, 15],
    10: [5, 10, 20, 40, 25],
}

# Estimated from final boards (see paper, section 4)
H = {1: 3.7638, 2: 4.3420, 3: 3.4406, 4: 2.5010, 5: 1.8642}
BG = {1: 0.0809, 2: 0.0666, 3: 0.1776, 4: 0.3551, 5: 0.2340}


def pool_total(cost: int) -> int:
    return COPIES[cost] * CHAMPS[cost]


def feasible(cost: int, star: int, competitors: int, h: float | None = None) -> bool:
    """The pool must still hold enough copies after the competitors' share."""
    h = H[cost] if h is None else h
    return COPIES[cost] - competitors * h >= NEED[star] - 1e-9


def hit_prob(level, cost, owned, competitors, h=None, bg=None) -> float:
    h = H[cost] if h is None else h
    bg = BG[cost] if bg is None else bg
    left = COPIES[cost] - competitors * h - owned
    if left <= 0:
        return 0.0
    other = (pool_total(cost) - COPIES[cost]) * (1 - bg)
    return ODDS[level][cost - 1] / 100 * left / (left + other)


def _check(level, cost, star, owned):
    if level not in ODDS:
        raise ValueError("level must be 1 to 10")
    if cost not in COPIES:
        raise ValueError("cost must be 1 to 5")
    if star not in NEED:
        raise ValueError("star must be 2 or 3")
    if not 0 <= owned < NEED[star]:
        raise ValueError("owned copies must be below the copies needed")


def expected_shops(level, cost, star, competitors, owned=0, h=None, bg=None) -> float:
    _check(level, cost, star, owned)
    if not feasible(cost, star, competitors, h) or ODDS[level][cost - 1] == 0:
        return float("inf")
    n = NEED[star] - owned
    Q = np.zeros((n, n))
    for i in range(n):
        p = hit_prob(level, cost, owned + i, competitors, h, bg)
        for j in range(SLOTS + 1):
            if i + j < n:
                Q[i, i + j] += comb(SLOTS, j) * p**j * (1 - p) ** (SLOTS - j)
    return float(np.linalg.solve(np.eye(n) - Q, np.ones(n))[0])


def expected_gold(level, cost, star, competitors, owned=0, h=None, bg=None) -> float:
    """Expected gold: 2 per reroll (first shop of a round is free) plus copy prices."""
    shops = expected_shops(level, cost, star, competitors, owned, h, bg)
    if np.isinf(shops):
        return float("inf")
    return REROLL_COST * (shops - 1) + cost * (NEED[star] - owned)


def simulate_gold(level, cost, star, competitors, owned=0, h=None, bg=None,
                  n=20000, seed=0, max_shops=20000) -> np.ndarray:
    """Monte Carlo draws of the gold spent; inf when the upgrade is infeasible."""
    _check(level, cost, star, owned)
    if not feasible(cost, star, competitors, h) or ODDS[level][cost - 1] == 0:
        return np.full(n, np.inf)
    m = NEED[star] - owned
    probs = np.array([hit_prob(level, cost, owned + i, competitors, h, bg) for i in range(m)])
    rng = np.random.default_rng(seed)
    state = np.zeros(n, dtype=int)
    shops = np.zeros(n, dtype=int)
    alive = np.ones(n, dtype=bool)
    for _ in range(max_shops):
        idx = np.flatnonzero(alive)
        if idx.size == 0:
            break
        state[idx] = np.minimum(m, state[idx] + rng.binomial(SLOTS, probs[state[idx]]))
        shops[idx] += 1
        alive[idx] = state[idx] < m
    return REROLL_COST * (shops - 1) + cost * m
