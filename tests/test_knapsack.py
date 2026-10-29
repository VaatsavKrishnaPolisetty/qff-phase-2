"""Unit tests for Knapsack QUBO construction, Ising mapping, and baseline metrics."""

import pytest
import numpy as np
from src import knapsack as K
from src import qaoa_numpy as Qn

def test_classical_optimum():
    """Verify ground truth exhaustive search values match locked instance."""
    assert K.V_STAR == 26
    assert K.items_from_index(K.OPT_INDEX) == [1, 2, 3, 4]
    assert K.ITEM_WEIGHT[K.OPT_INDEX] == 14
    assert K.N_FEASIBLE_SUBSETS == 28

def test_qubo_cost_direct_and_matrix_equivalence():
    """Verify QUBO cost matrix reproduces direct penalty formulation across state space."""
    Q, const = K.build_qubo()
    assert Q.shape == (9, 9)
    # Sample test representative bitstrings including boundaries
    for b in [0, K.OPT_INDEX, K.QUBO_MIN_INDEX, (1 << 9) - 1]:
        y = K.bits(b, K.N_QUBITS)
        matrix_cost = y @ Q @ y + const
        direct_cost = K.qubo_cost_direct(y)
        assert abs(matrix_cost - direct_cost) < 1e-9

def test_qubo_minimum_matches_optimal_item():
    """Verify global minimum of QUBO corresponds to optimal item selection."""
    min_idx = K.QUBO_MIN_INDEX
    item_part = min_idx & K.ITEM_MASK
    assert item_part == K.OPT_INDEX
    assert K.COST[min_idx] == -26.0

def test_ising_equivalence():
    """Verify Ising Hamiltonian matches QUBO cost on all 512 basis states."""
    h, J, off = K.to_ising()
    assert len(J) == 36  # Fully connected 9-qubit two-body terms
    diag = K.ising_diag(h, J, off)
    assert np.allclose(diag, K.COST)

def test_random_baseline():
    """Verify random baseline feasibility and optimality probabilities."""
    rb = K.random_baseline()
    assert rb["p_feasible"] == 0.875
    assert abs(rb["p_opt"] - 1.0 / 32.0) < 1e-12

def test_qaoa_statevector_probabilities():
    """Verify QAOA probability vector sums to 1.0."""
    h, J, off = K.to_ising()
    scale = K.ising_scale(h, J)
    diag_scaled = (K.COST - off) / scale
    probs = Qn.probabilities(gamma=0.35, beta=0.45, diag_scaled=diag_scaled)
    assert abs(probs.sum() - 1.0) < 1e-12
    assert np.all(probs >= 0.0)

