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


# ----------------------------------------------------------------- CVaR QAOA
def cvar_cost(params, diag_scaled: np.ndarray, alpha: float = 0.1) -> float:
    """Conditional Value-at-Risk expectation (Rockafellar–Uryasev formulation).

    Sorts states by cost descending (worst first), takes the worst *alpha* fraction
    of the probability mass, and returns their probability-weighted average cost.
    Smaller alpha  =>  optimizer focuses on the tail  =>  pushes probability
    toward low-cost (good) states.  alpha=1  reproduces the standard expectation.
    """
    p = probabilities(params[0], params[1], diag_scaled)
    idx = np.argsort(-diag_scaled)          # worst (highest cost) first
    sp, sc = p[idx], diag_scaled[idx]
    cum = np.cumsum(sp)
    k = int(np.searchsorted(cum, alpha, side="left"))
    k = min(k, len(sp) - 1)
    if k == 0:
        return float(sc[0])
    weighted = float(np.dot(sp[:k], sc[:k]))
    residual = alpha - cum[k - 1]
    if residual > 0:
        weighted += residual * sc[k]
    return weighted / alpha


def optimise_cvar(diag_scaled: np.ndarray, seeds=SEEDS, alpha: float = 0.1,
                  maxiter: int = MAXITER):
    """Run COBYLA with the CVaR cost function instead of the standard expectation."""
    runs = []
    for seed in seeds:
        g0, b0 = initial_angles(seed)
        res = minimize(cvar_cost, x0=[g0, b0], args=(diag_scaled, alpha),
                       method="COBYLA", options={"maxiter": maxiter})
        g, b = float(res.x[0]), float(res.x[1])
        ev = K.evaluate_probs(probabilities(g, b, diag_scaled))
        runs.append(dict(seed=seed, gamma0=g0, beta0=b0, gamma=g, beta=b,
                         cvar_expectation=float(res.fun), nfev=int(res.nfev),
                         alpha=alpha,
                         p_feasible_exact=ev["p_feasible"], p_opt_exact=ev["p_opt"]))
    best = min(runs, key=lambda r: r["cvar_expectation"])
    return runs, best


# ----------------------------------------------------------------- Constraint-Preserving Mixer QAOA
#  The constraint  c^T y = 15  is preserved by XY swaps on pairs with equal c_i.
#  c = [5,3,4,2,6,1,2,4,8]  ->  equal pairs: (2,7) both weight 4, (3,6) both weight 2.
#  The initial state is a uniform superposition over the 28 feasible states
#  (item subset + exact slack), so P_feasible starts at 100 % and the mixer keeps it there.

CP_EQUAL_PAIRS = [(2, 7), (3, 6)]      # qubit pairs with equal constraint coefficients


def _feasible_initial_state() -> np.ndarray:
    """Uniform superposition over constraint-satisfying 9-qubit basis states."""
    psi = np.zeros(1 << K.N_QUBITS, dtype=complex)
    for item_idx in range(1 << K.N_ITEMS):
        if K.ITEM_FEASIBLE[item_idx]:
            weight = int(K.ITEM_WEIGHT[item_idx])
            slack = K.CAPACITY - weight       # exact slack 0..15, binary-encodable
            full = item_idx | (slack << K.N_ITEMS)
            psi[full] = 1.0
    return psi / np.linalg.norm(psi)


def _apply_xy(psi: np.ndarray, i: int, j: int, beta: float) -> np.ndarray:
    """Apply exp(-i beta (X_i X_j + Y_i Y_j)) to statevector psi.

    This is the XY / partial-swap gate: it rotates the |...0_i 1_j...> and
    |...1_i 0_j...> subspace by cos(2beta)/-i sin(2beta) and leaves |00> and |11> alone.
    """
    psi = psi.astype(complex).copy()
    c, s = np.cos(2 * beta), -1j * np.sin(2 * beta)
    for state in range(len(psi)):
        bi = (state >> i) & 1
        bj = (state >> j) & 1
        if bi == 0 and bj == 1:                      # process |01> states only
            partner = state ^ (1 << i) ^ (1 << j)    # -> |10>
            a, b = psi[state], psi[partner]
            psi[state] = c * a + s * b
            psi[partner] = s * a + c * b
    return psi


def cp_probabilities(gamma: float, beta: float, diag_scaled: np.ndarray,
                     equal_pairs=CP_EQUAL_PAIRS) -> np.ndarray:
    """QAOA probabilities with a constraint-preserving XY mixer.

    Initial state = uniform superposition over feasible states.
    Cost layer = same as standard QAOA.
    Mixer = RXX+RYY on equal-coefficient pairs (preserves c^T y = W).
    """
    n = int(np.round(np.log2(len(diag_scaled))))
    psi = _feasible_initial_state()
    psi = psi * np.exp(-1j * gamma * diag_scaled)   # cost layer
    for i, j in equal_pairs:
        psi = _apply_xy(psi, i, j, beta)             # constraint-preserving mixer
    return np.abs(psi) ** 2


def optimise_cp(diag_scaled: np.ndarray, seeds=SEEDS,
                equal_pairs=CP_EQUAL_PAIRS, maxiter: int = MAXITER):
    """Optimise the constraint-preserving-mixer QAOA from seeded starts."""
    runs = []
    for seed in seeds:
        g0, b0 = initial_angles(seed)
        def cost(params):
            p = cp_probabilities(params[0], params[1], diag_scaled, equal_pairs)
            return float(p @ diag_scaled)
        res = minimize(cost, x0=[g0, b0], method="COBYLA", options={"maxiter": maxiter})
        g, b = float(res.x[0]), float(res.x[1])
        p = cp_probabilities(g, b, diag_scaled, equal_pairs)
        ev = K.evaluate_probs(p)
        runs.append(dict(seed=seed, gamma0=g0, beta0=b0, gamma=g, beta=b,
                         expectation=float(res.fun), nfev=int(res.nfev),
                         p_feasible_exact=ev["p_feasible"], p_opt_exact=ev["p_opt"]))
    best = min(runs, key=lambda r: r["expectation"])
    return runs, best


# ----------------------------------------------------------------- Multi-Angle QAOA (ma-QAOA)
#  Standard p=1 uses one gamma for all ZZ terms and one beta for all qubits.
#  ma-QAOA gives each single-qubit RZ, each two-qubit RZZ, and each mixer RX its
#  own variational parameter: n + len(J) + n = 9 + 36 + 9 = 54 parameters.

_MA_N_PARAMS = None  # cached count


def ma_qaoa_probabilities(params: np.ndarray, h: np.ndarray, J: dict, scale: float,
                          n: int = K.N_QUBITS) -> np.ndarray:
    """Multi-angle QAOA probabilities.

    params layout (length n + len(J) + n):
        [0, n)              -> single-qubit gamma_i  (for RZ)
        [n, n+len(J))       -> pair gamma_ij         (for RZZ)
        [n+len(J), end)     -> mixer beta_i          (for RX)
    """
    n_pairs = len(J)
    gammas_s = params[:n]
    gammas_p = params[n:n + n_pairs]
    betas = params[n + n_pairs:]

    # Z eigenvalues for every basis state: z_i(b) = (-1)^{bit_i(b)}
    z = 1 - 2 * K._ALL_BITS                                   # shape (512, 9)

    # Build the diagonal cost phase (all Z and ZZ operators commute)
    phase = np.zeros(1 << n)
    for i in range(n):
        if h[i] != 0:
            phase += gammas_s[i] * h[i] * z[:, i] / scale
    for idx, ((i, j), v) in enumerate(J.items()):
        phase += gammas_p[idx] * v * z[:, i] * z[:, j] / scale

    psi = np.full(1 << n, 1.0 / np.sqrt(1 << n), dtype=complex)
    psi = psi * np.exp(-1j * phase)

    # Per-qubit RX mixer
    psi = psi.reshape([2] * n)
    for ax in range(n):
        c, s = np.cos(betas[ax]), -1j * np.sin(betas[ax])
        psi = c * psi + s * np.flip(psi, axis=ax)
    return np.abs(psi.reshape(-1)) ** 2


def optimise_ma_qaoa(diag_scaled: np.ndarray, h: np.ndarray, J: dict, scale: float,
                     gamma_init: float = 0.2831, beta_init: float = 2.8648,
                     seeds=SEEDS, maxiter: int = 500):
    """Optimise ma-QAOA with 54 parameters, warm-started from standard QAOA angles."""
    n = K.N_QUBITS
    n_pairs = len(J)
    n_total = n + n_pairs + n

    def cost(params):
        p = ma_qaoa_probabilities(params, h, J, scale, n)
        return float(p @ diag_scaled)

    runs = []
    for seed in seeds:
        # Warm start: all gammas = gamma_init, all betas = beta_init, plus small noise
        rng = np.random.default_rng(seed)
        x0 = np.concatenate([
            np.full(n, gamma_init) + rng.normal(0, 0.05, n),
            np.full(n_pairs, gamma_init) + rng.normal(0, 0.05, n_pairs),
            np.full(n, beta_init) + rng.normal(0, 0.05, n),
        ])
        res = minimize(cost, x0=x0, method="COBYLA", options={"maxiter": maxiter})
        p = ma_qaoa_probabilities(res.x, h, J, scale, n)
        ev = K.evaluate_probs(p)
        runs.append(dict(seed=seed, n_params=n_total,
                         expectation=float(res.fun), nfev=int(res.nfev),
                         p_feasible_exact=ev["p_feasible"], p_opt_exact=ev["p_opt"]))
    best = min(runs, key=lambda r: r["expectation"])
    return runs, best


# ----------------------------------------------------------------- CVaR + Constraint-Preserving Mixer Combined
def cvar_cp_cost(params, diag_scaled: np.ndarray, alpha: float = 0.1,
                 equal_pairs=CP_EQUAL_PAIRS) -> float:
    """CVaR cost evaluated on CP-mixer probabilities.

    Combines the two strongest individual techniques: the constraint-preserving
    XY mixer keeps P_feasible = 100 %, while the CVaR tail objective pushes
    probability toward the optimal state within the feasible subspace.
    """
    p = cp_probabilities(params[0], params[1], diag_scaled, equal_pairs)
    idx = np.argsort(-diag_scaled)
    sp, sc = p[idx], diag_scaled[idx]
    cum = np.cumsum(sp)
    k = int(np.searchsorted(cum, alpha, side="left"))
    k = min(k, len(sp) - 1)
    if k == 0:
        return float(sc[0])
    weighted = float(np.dot(sp[:k], sc[:k]))
    residual = alpha - cum[k - 1]
    if residual > 0:
        weighted += residual * sc[k]
    return weighted / alpha


def optimise_cvar_cp(diag_scaled: np.ndarray, seeds=SEEDS, alpha: float = 0.1,
                     equal_pairs=CP_EQUAL_PAIRS, maxiter: int = MAXITER):
    """Optimise CVaR-cost QAOA with the constraint-preserving mixer."""
    runs = []
    for seed in seeds:
        g0, b0 = initial_angles(seed)
        res = minimize(cvar_cp_cost, x0=[g0, b0],
                       args=(diag_scaled, alpha, equal_pairs),
                       method="COBYLA", options={"maxiter": maxiter})
        g, b = float(res.x[0]), float(res.x[1])
        p = cp_probabilities(g, b, diag_scaled, equal_pairs)
        ev = K.evaluate_probs(p)
        runs.append(dict(seed=seed, gamma=g, beta=b,
                         cvar_cp_cost=float(res.fun), alpha=alpha, nfev=int(res.nfev),
                         p_feasible_exact=ev["p_feasible"], p_opt_exact=ev["p_opt"]))
    best = min(runs, key=lambda r: r["cvar_cp_cost"])
    return runs, best
