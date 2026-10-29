"""Unit tests for QAOA and Bell state quantum circuits."""

import pytest
import numpy as np
from src import knapsack as K
from src import circuits as C
from src import bell as B
from src.processors import PROCESSOR_B

def test_qaoa_circuit_structure():
    """Verify QAOA circuit depth, qubits, and gate construction."""
    h, J, off = K.to_ising()
    scale = K.ising_scale(h, J)
    qc = C.build_qaoa_circuit(0.5, 0.3, h, J, scale=scale)
    assert qc.num_qubits == 9
    gate_counts = qc.count_ops()
    assert "rzz" in gate_counts
    assert "rx" in gate_counts

def test_bell_state_fidelity_formula():
    """Verify Bell state fidelity formula F = (1 + <XX> - <YY> + <ZZ>) / 4."""
    # Perfect Bell state (|00> + |11>) / sqrt(2) has <XX> = 1, <YY> = -1, <ZZ> = 1
    xx, yy, zz = 1.0, -1.0, 1.0
    f_perfect = (1 + xx - yy + zz) / 4
    assert abs(f_perfect - 1.0) < 1e-12

    # Completely mixed state has <XX> = 0, <YY> = 0, <ZZ> = 0 -> F = 0.25
    xx_m, yy_m, zz_m = 0.0, 0.0, 0.0
    f_mixed = (1 + xx_m - yy_m + zz_m) / 4
    assert abs(f_mixed - 0.25) < 1e-12

def test_processor_transpilation_basis_gates():
    """Verify that transpiling for Processor B restricts gates to official basis set."""
    h, J, off = K.to_ising()
    scale = K.ising_scale(h, J)
    qc = C.build_qaoa_circuit(0.4, 0.2, h, J, scale=scale)
    transpiled = C.transpile_official(qc, PROCESSOR_B)
    allowed_gates = set(PROCESSOR_B["basis_gates"])
    used_gates = set(transpiled.count_ops().keys()) - {"barrier", "measure"}
    assert used_gates.issubset(allowed_gates)
