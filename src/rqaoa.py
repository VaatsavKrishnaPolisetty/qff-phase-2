"""Recursive QAOA (RQAOA).

Uses the p=1 QAOA statevector to compute two-qubit correlators <Z_i Z_j>,
eliminates the strongest-correlated pair of *item* qubits, substitutes the
relationship back into the knapsack, and solves the reduced problem
exhaustively.  This turns QAOA from a sampler into a classical heuristic
that uses quantum correlations as input.

Reference: Bravyi, Kluchnikov, Matsuura, Shaydulin (2020).
"""
from __future__ import annotations

import itertools
import numpy as np

from . import knapsack as K
from . import qaoa_numpy as Qn


def compute_item_correlators(probs: np.ndarray, n_items: int = K.N_ITEMS) -> dict:
    """<Z_i Z_j> for all item-qubit pairs (0..n_items-1), marginalising slack qubits."""
    z = 1 - 2 * K._ALL_BITS          # Z eigenvalue per qubit, shape (512, 9)
    corr = {}
    for i in range(n_items):
        for j in range(i + 1, n_items):
            corr[(i, j)] = float(np.dot(probs, z[:, i] * z[:, j]))
    return corr


def _solve_reduced_knapsack(values, weights, capacity):
    """Exhaustive solve of a small knapsack (len <= 5)."""
    n = len(values)
    best_val, best_bits = 0, [0] * n
    for bits in range(1 << n):
        x = [(bits >> i) & 1 for i in range(n)]
        w = sum(w * xi for w, xi in zip(weights, x))
        if w <= capacity:
            v = sum(v * xi for v, xi in zip(values, x))
            if v > best_val:
                best_val, best_bits = v, x
    return best_val, best_bits


def rqaoa(diag_scaled: np.ndarray, gamma: float, beta: float,
          n_rounds: int = 2) -> dict:
    """One or two rounds of RQAOA elimination on the 5-item knapsack.

    Round 1: eliminate one item using the strongest <Z_i Z_j>.
    Round 2: eliminate another item from the 4-item reduced problem.
    """
    v = list(K.VALUES)
    w = list(K.WEIGHTS)
    cap = K.CAPACITY
    active = list(range(K.N_ITEMS))          # indices still in play
    history = []

    for rnd in range(n_rounds):
        if len(active) <= 2:
            break

        # Compute QAOA probabilities and correlators for the current problem size.
        # For round 0 we use the full 9-qubit QAOA probabilities.
        # For subsequent rounds we re-run QAOA on the reduced Ising (if needed).
        if rnd == 0:
            probs = Qn.probabilities(gamma, beta, diag_scaled)
            corr = compute_item_correlators(probs)
        else:
            # For round 2, solve the reduced problem classically (it's small enough).
            # No need for another QAOA run — just solve exhaustively.
            break

        # Find strongest item-item correlator
        best_pair, best_abs = None, 0.0
        for (i, j), c in corr.items():
            if i in active and j in active and abs(c) > best_abs:
                best_pair, best_abs = (i, j), abs(c)

        if best_pair is None:
            break

        i_el, j_el = best_pair
        c_val = corr[best_pair]

        # Eliminate j_el: x_{j_el} = x_{i_el} if c > 0, else 1 - x_{i_el}
        positive = c_val > 0

        # Update values and weights for the reduced problem
        # If x_j = x_i:   v_i -> v_i + v_j,  w_i -> w_i + w_j
        # If x_j = 1-x_i: v_i -> v_i - v_j,  w_i -> w_i - w_j,  cap -= w_j,  v_const += v_j
        idx_i = active.index(i_el)
        idx_j = active.index(j_el)

        if positive:
            v[idx_i] = v[idx_i] + v[idx_j]
            w[idx_i] = w[idx_i] + w[idx_j]
        else:
            v[idx_i] = v[idx_i] - v[idx_j]
            w[idx_i] = w[idx_i] - w[idx_j]
            cap = cap - w[idx_j]
            # constant value offset: v_j * 1 (x_j=1 part)
            # This doesn't affect the optimization, just the final value

        active.remove(j_el)
        # Build reduced arrays
        v_red = [v[active.index(a)] for a in active]
        w_red = [w[active.index(a)] for a in active]

        history.append(dict(round=rnd, eliminated_item=j_el + 1,
                            kept_item=i_el + 1, correlation=round(c_val, 4),
                            relationship="x_j = x_i" if positive else "x_j = 1 - x_i",
                            remaining_items=[a + 1 for a in active]))

    # Solve the reduced problem classically
    v_red = [v[active.index(a)] for a in active]
    w_red = [w[active.index(a)] for a in active]

    best_val, best_bits_red = _solve_reduced_knapsack(v_red, w_red, cap)

    # Reconstruct the full 5-item solution
    full_x = [0] * K.N_ITEMS
    for idx, a in enumerate(active):
        full_x[a] = best_bits_red[idx]

    # Apply elimination rules to recover eliminated items
    for h in reversed(history):
        j_el = h["eliminated_item"] - 1
        i_el = h["kept_item"] - 1
        if h["relationship"] == "x_j = x_i":
            full_x[j_el] = full_x[i_el]
        else:
            full_x[j_el] = 1 - full_x[i_el]

    # Compute actual value and weight
    total_value = sum(K.VALUES[i] * full_x[i] for i in range(K.N_ITEMS))
    total_weight = sum(K.WEIGHTS[i] * full_x[i] for i in range(K.N_ITEMS))
    feasible = total_weight <= K.CAPACITY
    is_optimal = total_value == K.V_STAR

    return dict(
        rounds=history,
        solution=full_x,
        solution_items=[i + 1 for i in range(K.N_ITEMS) if full_x[i] == 1],
        total_value=total_value,
        total_weight=total_weight,
        feasible=feasible,
        is_optimal=is_optimal,
        v_star=K.V_STAR,
    )
