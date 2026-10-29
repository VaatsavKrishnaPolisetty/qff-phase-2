"""Exact p=1 QAOA statevector simulation in NumPy (used to optimise gamma, beta).

Conventions match the Qiskit circuit in circuits.py:
    cost layer  exp(-i gamma C_scaled)   <->  RZ(2 gamma h_i/scale), RZZ(2 gamma J_ij/scale)
    mixer       exp(-i beta X) per qubit <->  RX(2 beta)
    C_scaled = (cost - const) / scale  (a constant only adds a global phase)
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize

from . import knapsack as K

OPTIMIZER_NAME = "COBYLA (scipy)"
MAXITER = 200
SEEDS = (0, 1, 2, 3, 4)


def qaoa_state(gamma: float, beta: float, diag_scaled: np.ndarray, n: int | None = None) -> np.ndarray:
    if n is None:
        n = int(np.round(np.log2(len(diag_scaled))))
    psi = np.full(1 << n, 1.0 / np.sqrt(1 << n), dtype=complex)
    psi = psi * np.exp(-1j * gamma * diag_scaled)
    c, s = np.cos(beta), -1j * np.sin(beta)
    psi = psi.reshape([2] * n)
    for ax in range(n):                       # exp(-i beta X) on every qubit
        psi = c * psi + s * np.flip(psi, axis=ax)
    return psi.reshape(-1)


def probabilities(gamma: float, beta: float, diag_scaled: np.ndarray) -> np.ndarray:
    return np.abs(qaoa_state(gamma, beta, diag_scaled)) ** 2


def expectation(params, diag_scaled: np.ndarray) -> float:
    """<C_scaled> for params = (gamma, beta)."""
    p = probabilities(params[0], params[1], diag_scaled)
    return float(p @ diag_scaled)


def initial_angles(seed: int) -> tuple[float, float]:
    """gamma, beta ~ U[0, pi] drawn with numpy default_rng(seed) (kit rule)."""
    g, b = np.random.default_rng(seed).uniform(0.0, np.pi, size=2)
    return float(g), float(b)


def optimise_seeds(diag_scaled: np.ndarray, seeds=SEEDS, maxiter: int = MAXITER):
    """Run COBYLA from each seeded start. Cost is evaluated with an EXACT statevector.

    Returns (list of per-seed dicts, best dict).
    """
    runs = []
    for seed in seeds:
        g0, b0 = initial_angles(seed)
        res = minimize(expectation, x0=[g0, b0], args=(diag_scaled,),
                       method="COBYLA", options={"maxiter": maxiter})
        g, b = float(res.x[0]), float(res.x[1])
        ev = K.evaluate_probs(probabilities(g, b, diag_scaled))
        runs.append(dict(seed=seed, gamma0=g0, beta0=b0, gamma=g, beta=b,
                         expectation=float(res.fun), nfev=int(res.nfev),
                         p_feasible_exact=ev["p_feasible"], p_opt_exact=ev["p_opt"]))
    best = min(runs, key=lambda r: r["expectation"])
    return runs, best


def landscape_exact(diag_scaled: np.ndarray, gammas: np.ndarray, betas: np.ndarray,
                    observable: np.ndarray | None = None) -> np.ndarray:
    """Noise-free expectation on a (len(betas), len(gammas)) grid.

    The state is built with the scaled cost diagonal; `observable` (default: the same diagonal)
    is what gets averaged, e.g. pass the true QUBO cost K.COST to compare with the sampled plot.
    """
    obs = diag_scaled if observable is None else observable
    Z = np.zeros((len(betas), len(gammas)))
    for i, b in enumerate(betas):
        for j, g in enumerate(gammas):
            Z[i, j] = float(probabilities(g, b, diag_scaled) @ obs)
    return Z
