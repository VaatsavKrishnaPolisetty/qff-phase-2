"""PS-O3 knapsack: locked instance, exact classical solution, QUBO, Ising, metrics.

Pure NumPy (no Qiskit needed), so everything here can be tested anywhere.

Bit-order convention (same as Qiskit):
    a bitstring is stored as an integer b; qubit i is bit i of b, i.e. (b >> i) & 1.
    qubits 0-4 = items 1-5, qubits 5-8 = slack bits s0..s3 (weights 1, 2, 4, 8).
    A Qiskit count key such as '011110000' read right-to-left gives qubit 0 first,
    and int(key, 2) gives exactly this integer b.
"""
from __future__ import annotations

import numpy as np

# ----------------------------------------------------------------- locked instance
VALUES = np.array([10, 4, 7, 5, 8])      # item n = qubit n-1
WEIGHTS = np.array([5, 3, 4, 2, 6])
CAPACITY = 15
PENALTY = 5                              # P = 5 (required for the official rows)
N_ITEMS = 5
N_SLACK = 4                              # s = s0 + 2 s1 + 4 s2 + 8 s3  (0..15)
N_QUBITS = N_ITEMS + N_SLACK             # 9
COEF = np.concatenate([WEIGHTS, [1, 2, 4, 8]])        # coefficient of each qubit in the constraint
VAL9 = np.concatenate([VALUES, np.zeros(N_SLACK)])    # slack qubits carry no value
ITEM_MASK = (1 << N_ITEMS) - 1                         # 0b11111


def bits(index: int, n: int) -> np.ndarray:
    """Little-endian bit vector of an integer: element i is qubit i."""
    return np.array([(index >> i) & 1 for i in range(n)])


def items_from_index(item_index: int) -> list[int]:
    """1-based item numbers contained in an item-subset index."""
    return [i + 1 for i in range(N_ITEMS) if (item_index >> i) & 1]


# ----------------------------------------------------------------- exact classical solution
_ITEM_BITS = ((np.arange(1 << N_ITEMS)[:, None] >> np.arange(N_ITEMS)) & 1)
ITEM_WEIGHT = _ITEM_BITS @ WEIGHTS                     # weight of each of the 32 subsets
ITEM_VALUE = _ITEM_BITS @ VALUES                       # value of each of the 32 subsets
ITEM_FEASIBLE = ITEM_WEIGHT <= CAPACITY


def exhaustive_search():
    """Exhaustive search over all 32 item subsets.

    Returns (table, best) where table is a list of dicts and best is the optimal feasible one.
    """
    table = []
    for idx in range(1 << N_ITEMS):
        table.append(dict(index=idx, items=items_from_index(idx),
                          value=int(ITEM_VALUE[idx]), weight=int(ITEM_WEIGHT[idx]),
                          feasible=bool(ITEM_FEASIBLE[idx])))
    feasible = [r for r in table if r["feasible"]]
    best = max(feasible, key=lambda r: (r["value"], -r["weight"]))
    return table, best


_TABLE, _BEST = exhaustive_search()
V_STAR = _BEST["value"]            # 26
OPT_INDEX = _BEST["index"]         # item bits of the optimal subset (items 1,2,3,4 -> 0b01111 = 15)
N_FEASIBLE_SUBSETS = int(ITEM_FEASIBLE.sum())   # 28 of 32


# ----------------------------------------------------------------- QUBO
def build_qubo():
    """Upper-triangular Q and constant such that  cost(y) = y^T Q y + const.

    cost(y) = - sum v_i x_i + P (sum c_i y_i - W)^2 ,  y_i^2 = y_i
    diag  Q_ii = -v_i + P (c_i^2 - 2 W c_i)
    off   Q_ij = 2 P c_i c_j        (i < j)
    const = P W^2
    """
    Q = np.zeros((N_QUBITS, N_QUBITS))
    for i in range(N_QUBITS):
        Q[i, i] = -VAL9[i] + PENALTY * (COEF[i] ** 2 - 2 * CAPACITY * COEF[i])
        for j in range(i + 1, N_QUBITS):
            Q[i, j] = 2 * PENALTY * COEF[i] * COEF[j]
    return Q, PENALTY * CAPACITY ** 2


def qubo_cost_direct(y) -> float:
    """The formula exactly as written in the kit (used to verify the matrix)."""
    y = np.asarray(y)
    return float(-VAL9 @ y + PENALTY * (COEF @ y - CAPACITY) ** 2)


_ALL_BITS = ((np.arange(1 << N_QUBITS)[:, None] >> np.arange(N_QUBITS)) & 1)


def cost_table() -> np.ndarray:
    """QUBO cost of every one of the 512 bitstrings, indexed by the integer b."""
    return -_ALL_BITS @ VAL9 + PENALTY * (_ALL_BITS @ COEF - CAPACITY) ** 2


COST = cost_table()
QUBO_MIN_INDEX = int(np.argmin(COST))


# ----------------------------------------------------------------- Ising
def to_ising(Q=None, const=None):
    """cost = offset + sum_i h_i Z_i + sum_{i<j} J_ij Z_i Z_j     with y_i = (1 - Z_i)/2."""
    if Q is None:
        Q, const = build_qubo()
    n = len(Q)
    h = np.zeros(n)
    J = {}
    offset = float(const)
    for i in range(n):
        offset += Q[i, i] / 2
        h[i] -= Q[i, i] / 2
        for j in range(i + 1, n):
            q = Q[i, j]
            if q == 0:
                continue
            offset += q / 4
            h[i] -= q / 4
            h[j] -= q / 4
            J[(i, j)] = q / 4
    return h, J, offset


def ising_scale(h, J) -> float:
    """Largest coefficient magnitude (Hamiltonian is divided by this; see README)."""
    return float(max(np.abs(h).max(), max(abs(v) for v in J.values())))


def ising_diag(h, J, offset) -> np.ndarray:
    """Diagonal of the Ising Hamiltonian for all 512 basis states (should equal COST)."""
    z = 1 - 2 * _ALL_BITS                         # Z eigenvalue of each qubit
    e = offset + z @ h
    for (i, j), v in J.items():
        e = e + v * z[:, i] * z[:, j]
    return e


# ----------------------------------------------------------------- metrics from samples
def evaluate_probs(probs: np.ndarray) -> dict:
    """Exact metrics for a probability vector over the 512 bitstrings (or 32 for item qubits)."""
    probs = np.asarray(probs, dtype=float)
    if len(probs) == (1 << N_ITEMS):
        return dict(p_feasible=float(probs[ITEM_FEASIBLE].sum()),
                    p_opt=float(probs[OPT_INDEX]),
                    mean_qubo_cost=float(probs @ -ITEM_VALUE))
    item_idx = np.arange(1 << N_QUBITS) & ITEM_MASK
    feas = ITEM_FEASIBLE[item_idx]
    return dict(p_feasible=float(probs[feas].sum()),
                p_opt=float(probs[item_idx == OPT_INDEX].sum()),
                mean_qubo_cost=float(probs @ COST))


def evaluate_counts(counts: dict) -> dict:
    """Judge a sampled run exactly as the kit defines it.

    Feasibility and value use the 5 ITEM bits only (slack bits ignored).
    """
    shots = int(sum(counts.values()))
    feas_shots = 0
    opt_shots = 0
    cost_sum = 0.0
    subset_counts = np.zeros(1 << N_ITEMS, dtype=int)   # samples per item subset (slack summed out)
    for key, c in counts.items():
        b = int(key.replace(" ", ""), 2)
        it = b & ITEM_MASK
        subset_counts[it] += c
        cost_sum += COST[b] * c
        if ITEM_FEASIBLE[it]:
            feas_shots += c
        if it == OPT_INDEX:
            opt_shots += c

    seen_feasible = [it for it in range(1 << N_ITEMS) if subset_counts[it] > 0 and ITEM_FEASIBLE[it]]
    if seen_feasible:
        best = max(seen_feasible, key=lambda it: (ITEM_VALUE[it], -ITEM_WEIGHT[it]))
        top = max(seen_feasible, key=lambda it: subset_counts[it])
        best_val, best_w = int(ITEM_VALUE[best]), int(ITEM_WEIGHT[best])
        best_items, top_items = items_from_index(best), items_from_index(top)
        top_val = int(ITEM_VALUE[top])
    else:
        best_val, best_w, best_items, top_items, top_val = 0, 0, [], [], 0
    return dict(shots=shots,
                p_feasible=feas_shots / shots,
                p_opt=opt_shots / shots,
                best_feasible_value=best_val,
                best_feasible_weight=best_w,
                best_feasible_items=best_items,
                pct_optimal=100.0 * best_val / V_STAR,
                most_sampled_feasible_items=top_items,
                most_sampled_feasible_value=top_val,
                mean_qubo_cost=cost_sum / shots)


def random_baseline() -> dict:
    """Uniform random guessing over all 512 bitstrings, computed exactly by enumeration."""
    base = evaluate_probs(np.full(1 << N_QUBITS, 1.0 / (1 << N_QUBITS)))
    base["expected_item_value_if_feasible"] = float(ITEM_VALUE[ITEM_FEASIBLE].mean())
    # prob. that the optimal subset is seen at least once in 4096 random shots:
    base["p_best_feasible_is_optimal_in_4096_shots"] = float(1 - (1 - base["p_opt"]) ** 4096)
    return base
