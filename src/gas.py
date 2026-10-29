"""Grover Adaptive Search (GAS).

A fundamentally different quantum algorithm: instead of a variational ansatz,
use Grover amplitude amplification to find low-cost states.  The algorithm:

1. Start with a cost threshold (e.g. median QUBO cost).
2. Build a phase oracle marking states with cost < threshold.
3. Apply Grover diffusion to amplify marked states.
4. Sample, update threshold to the best cost found.
5. Repeat until the optimal state is found.

Statevector implementation (exact, 512-dim): the oracle and diffusion
are element-wise or sum operations, so each Grover iteration is O(N).
"""
from __future__ import annotations

import numpy as np

from . import knapsack as K


def _grover_oracle(psi: np.ndarray, costs: np.ndarray, threshold: float) -> np.ndarray:
    """Phase oracle: flip the sign of amplitudes for states with cost < threshold."""
    psi = psi.copy()
    psi[costs < threshold] *= -1
    return psi


def _grover_diffusion(psi: np.ndarray, n: int) -> np.ndarray:
    """Diffusion operator 2|s><s| - I  where |s> = |+>^n."""
    N = 1 << n
    s = np.sum(psi)
    return (2 * s / N) * np.ones(N, dtype=complex) - psi


def _optimal_grover_iters(n_marked: int, n_total: int) -> int:
    """Optimal number of Grover iterations for n_marked / n_total."""
    if n_marked == 0 or n_marked >= n_total:
        return 0
    ratio = n_marked / n_total
    return max(1, int(np.floor(np.pi / 4 / np.sqrt(ratio))))


def gas_search(costs: np.ndarray, n: int = K.N_QUBITS,
               max_rounds: int = 30, seed: int = 42,
               n_shots: int = 4096) -> dict:
    """Run Grover Adaptive Search on the QUBO cost table.

    Returns the best state found, its cost, and the full search history.
    """
    rng = np.random.default_rng(seed)
    N = 1 << n
    opt_cost = float(costs.min())
    opt_index = int(np.argmin(costs))

    # Initial threshold: median cost (roughly half the states are marked)
    threshold = float(np.median(costs))
    best_cost = float("inf")
    best_state = -1
    history = []

    for rnd in range(max_rounds):
        # Reset to uniform superposition
        psi = np.full(N, 1.0 / np.sqrt(N), dtype=complex)

        # Determine marked set and optimal Grover iterations
        n_marked = int((costs < threshold).sum())
        if n_marked == 0:
            # No states below threshold — relax threshold
            threshold = float(np.sort(costs)[1])
            n_marked = int((costs < threshold).sum())

        n_iters = _optimal_grover_iters(n_marked, N)
        n_iters = min(n_iters, 50)  # cap for safety

        # Apply Grover iterations
        for _ in range(n_iters):
            psi = _grover_oracle(psi, costs, threshold)
            psi = _grover_diffusion(psi, n)

        # Sample from the amplified state
        probs = np.abs(psi) ** 2
        probs = probs / probs.sum()  # renormalise (numerical safety)
        sampled = rng.choice(N, p=probs)
        sampled_cost = float(costs[sampled])

        if sampled_cost < best_cost:
            best_cost = sampled_cost
            best_state = int(sampled)

        # Update threshold
        if sampled_cost < threshold:
            threshold = sampled_cost

        # Evaluate metrics on the sampled distribution
        # Simulate n_shots from the distribution
        shots = rng.choice(N, size=n_shots, p=probs)
        item_mask = K.ITEM_MASK
        feas_shots = sum(1 for s in shots if K.ITEM_FEASIBLE[int(s) & item_mask])
        opt_shots = sum(1 for s in shots if int(s) & item_mask == K.OPT_INDEX)

        history.append(dict(round=rnd, threshold=round(threshold, 2),
                             sampled_cost=round(sampled_cost, 2),
                             best_cost=round(best_cost, 2),
                             n_marked=n_marked, n_grover_iters=n_iters,
                             p_feasible=round(feas_shots / n_shots, 4),
                             p_opt=round(opt_shots / n_shots, 4)))

        if best_cost <= opt_cost:
            break

    # Final evaluation: P_opt from the best round's distribution
    # Recompute the best distribution
    psi = np.full(N, 1.0 / np.sqrt(N), dtype=complex)
    final_threshold = best_cost if best_cost < float("inf") else threshold
    n_marked = max(1, int((costs <= final_threshold).sum()))
    n_iters = _optimal_grover_iters(n_marked, N)
    for _ in range(n_iters):
        psi = _grover_oracle(psi, costs, final_threshold)
        psi = _grover_diffusion(psi, n)
    probs = np.abs(psi) ** 2
    probs = probs / probs.sum()
    p_opt = float(probs[opt_index])
    p_feasible = float(K.evaluate_probs(probs)["p_feasible"])

    return dict(
        best_state=best_state,
        best_cost=best_cost,
        best_items=K.items_from_index(best_state & K.ITEM_MASK) if best_state >= 0 else [],
        is_optimal=best_cost <= opt_cost,
        rounds_used=len(history),
        final_p_opt=round(p_opt, 4),
        final_p_feasible=round(p_feasible, 4),
        optimal_cost=opt_cost,
        history=history,
    )
