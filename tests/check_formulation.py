"""Fast self-check of the PS-O3 formulation. Run:  python tests/check_formulation.py
No Qiskit required. All asserts must pass before you trust any quantum result."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src import knapsack as K            # noqa: E402
from src import qaoa_numpy as Qn         # noqa: E402
from src.processors import PROCESSOR_A, PROCESSOR_B, make_processor_d, validate_processor_d  # noqa: E402

# 1. exact classical optimum
assert K.V_STAR == 26 and K.items_from_index(K.OPT_INDEX) == [1, 2, 3, 4]
assert K.ITEM_WEIGHT[K.OPT_INDEX] == 14 and K.N_FEASIBLE_SUBSETS == 28

# 2. QUBO matrix == kit formula on all 512 bitstrings
Q, const = K.build_qubo()
for b in range(1 << K.N_QUBITS):
    y = K.bits(b, K.N_QUBITS)
    assert abs(y @ Q @ y + const - K.qubo_cost_direct(y)) < 1e-9

# 3. QUBO minimum is the optimal item subset (slack makes the constraint tight: 14 + 1 = 15)
m = K.QUBO_MIN_INDEX
assert (m & K.ITEM_MASK) == K.OPT_INDEX and K.COST[m] == -26

# 4. Ising form reproduces the QUBO exactly
h, J, off = K.to_ising()
assert np.allclose(K.ising_diag(h, J, off), K.COST) and len(J) == 36

# 5. random baseline matches the rubric (0.875, 1/32)
rb = K.random_baseline()
assert rb["p_feasible"] == 0.875 and abs(rb["p_opt"] - 1 / 32) < 1e-12

# 6. QAOA statevector is normalised and the seeded optimisation runs
scale = K.ising_scale(h, J)
diag = (K.COST - off) / scale
assert abs(Qn.probabilities(0.3, 0.4, diag).sum() - 1) < 1e-12
runs, best = Qn.optimise_seeds(diag)
assert len(runs) == 5

# 7. processors
assert PROCESSOR_A["num_qubits"] == 5 < K.N_QUBITS            # A: not executable
assert PROCESSOR_B["num_qubits"] == 9
ok, _ = validate_processor_d(make_processor_d(9, [[i, (i + 1) % 9] for i in range(9)]), 9)
assert ok

print("ALL FORMULATION CHECKS PASSED")
print(f"V* = {K.V_STAR}, optimal items {K.items_from_index(K.OPT_INDEX)}, Hamiltonian scale = {scale}")
print(f"best seed {best['seed']}: gamma={best['gamma']:.4f} beta={best['beta']:.4f}, <C>={best['expectation']:.4f}")
