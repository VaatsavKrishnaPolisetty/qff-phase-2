"""Adaptive Penalty Scheduling (Homotopy Continuation).

Instead of jumping straight to P=5 (steep, narrow landscape where 3/5 seeds
get stuck), start at P=1 (smooth landscape), optimise, then warm-start each
successive P value from the previous optimum.  By the time we reach P=5 the
optimizer is already in the right valley.

Schedule: P = 1 -> 2 -> 3 -> 4 -> 5.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize

from . import knapsack as K
from . import qaoa_numpy as Qn


def _build_cost_table(penalty: float) -> np.ndarray:
    """QUBO cost table for all 512 bitstrings with a given penalty P."""
    return -K._ALL_BITS @ K.VAL9 + penalty * (K._ALL_BITS @ K.COEF - K.CAPACITY) ** 2


def _ising_from_penalty(penalty: float):
    """Build h, J, offset, scale, diag_scaled for a given penalty P."""
    Q = np.zeros((K.N_QUBITS, K.N_QUBITS))
    for i in range(K.N_QUBITS):
        Q[i, i] = -K.VAL9[i] + penalty * (K.COEF[i] ** 2 - 2 * K.CAPACITY * K.COEF[i])
        for j in range(i + 1, K.N_QUBITS):
            Q[i, j] = 2 * penalty * K.COEF[i] * K.COEF[j]
    const = penalty * K.CAPACITY ** 2
    h, J, offset = K.to_ising(Q, const)
    scale = K.ising_scale(h, J)
    cost_tbl = _build_cost_table(penalty)
    diag_scaled = (cost_tbl - offset) / scale
    return h, J, offset, scale, diag_scaled, cost_tbl


def adaptive_penalty_schedule(seeds=(0, 1, 2, 3, 4),
                               schedule=(1, 2, 3, 4, 5),
                               maxiter: int = 200):
    """Homotopy continuation from low penalty to P=5.

    For the first P value, run the standard 5-seed optimisation.
    For each subsequent P, warm-start from the previous optimum (single start).
    """
    results = []
    prev_g, prev_b = None, None

    for step, P_val in enumerate(schedule):
        h, J, off, scale, diag_scaled, cost_tbl = _ising_from_penalty(float(P_val))

        if prev_g is None:
            # First P: full 5-seed search
            runs, best = Qn.optimise_seeds(diag_scaled, seeds=seeds, maxiter=maxiter)
            g, b = best["gamma"], best["beta"]
            n_starts = len(seeds)
        else:
            # Warm start from previous P optimum
            # Scale gamma: landscape is in scaled units, so gamma transfers directly
            res = minimize(Qn.expectation, x0=[prev_g, prev_b],
                           args=(diag_scaled,), method="COBYLA",
                           options={"maxiter": maxiter})
            g, b = float(res.x[0]), float(res.x[1])
            n_starts = 1

        p = Qn.probabilities(g, b, diag_scaled)
        ev = K.evaluate_probs(p)
        qubo_min_valid = int((np.argmin(cost_tbl) & K.ITEM_MASK) == K.OPT_INDEX
                             and cost_tbl[np.argmin(cost_tbl)] == -K.V_STAR)

        results.append(dict(P=P_val, gamma=round(g, 4), beta=round(b, 4),
                            scale=round(scale, 1), n_starts=n_starts,
                            p_feasible=round(ev["p_feasible"], 4),
                            p_opt=round(ev["p_opt"], 4),
                            expectation=round(float(p @ diag_scaled), 4),
                            qubo_min_valid=qubo_min_valid))

        prev_g, prev_b = g, b

    return results
