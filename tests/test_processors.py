"""Unit tests for Processor A, B, and D specifications and validation rules."""

from pathlib import Path
import pytest
from src.processors import (
    PROCESSOR_A,
    PROCESSOR_B,
    load_processor,
    validate_processor_d,
)
from src import knapsack as K

def get_processor_d():
    p = Path(__file__).resolve().parent.parent / "processors" / "processor_D.json"
    return load_processor(p)

def test_processor_a_capacity_limit():
    """Verify Processor A has only 5 qubits and cannot fit 9-qubit problem."""
    assert PROCESSOR_A["num_qubits"] == 5
    assert PROCESSOR_A["num_qubits"] < K.N_QUBITS
    # Coupling edges: 4 undirected edges
    assert len(PROCESSOR_A["edges"]) == 4

def test_processor_b_properties():
    """Verify official reference Processor B specifications."""
    assert PROCESSOR_B["num_qubits"] == 9
    assert PROCESSOR_B["basis_gates"] == ["rz", "sx", "x", "cx"]
    assert len(PROCESSOR_B["edges"]) == 12

def test_processor_d_validation():
    """Verify frozen Processor D passes all official constraints."""
    proc_d = get_processor_d()
    assert proc_d["num_qubits"] >= 9 and proc_d["num_qubits"] <= 12
    assert proc_d["basis_gates"] == ["rz", "sx", "x", "cx"]

    # 1. Validate against internal validator function
    is_valid, msgs = validate_processor_d(proc_d, K.N_QUBITS)
    assert is_valid, f"Processor D internal validation failed: {msgs}"
    assert all(not m.startswith("FAIL") for m in msgs)

    # 2. Validate against official qff_phase2 validator function
    from qff_phase2 import validate_processor_d as official_validate
    official_errs = official_validate(proc_d, K.N_QUBITS)
    assert len(official_errs) == 0, f"Official validation errors: {official_errs}"

def test_processor_d_degree_limit():
    """Verify no qubit in Processor D exceeds maximum allowed degree of 4."""
    proc_d = get_processor_d()
    adjacency = {}
    for u, v in proc_d["edges"]:
        adjacency.setdefault(u, set()).add(v)
        adjacency.setdefault(v, set()).add(u)
    for q, neighbors in adjacency.items():
        assert len(neighbors) <= 4, f"Qubit {q} degree {len(neighbors)} exceeds limit 4!"
