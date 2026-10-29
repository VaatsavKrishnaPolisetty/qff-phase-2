"""Unit tests for the disaster relief case study and multi-constraint QUBO builder."""

import pytest
import numpy as np
from src.case_study import (
    DISASTER_RELIEF_ITEMS,
    build_multi_constraint_qubo,
    solve_case_study_brute_force,
    num_slack_bits,
)

def test_slack_qubit_count():
    """Verify log-binary slack qubit calculation."""
    assert num_slack_bits(0) == 0
    assert num_slack_bits(1) == 1
    assert num_slack_bits(3) == 2
    assert num_slack_bits(7) == 3
    assert num_slack_bits(15) == 4
    assert num_slack_bits(31) == 5

def test_disaster_relief_brute_force_ground_truth():
    """Verify classical ground truth on disaster-relief item values."""
    vals = [item["value"] for item in DISASTER_RELIEF_ITEMS]
    wgts = [item["weight"] for item in DISASTER_RELIEF_ITEMS]

    res = solve_case_study_brute_force(vals, wgts, max_weight=15)
    assert res["best_value"] == 26
    assert res["best_selection"] == [1, 1, 1, 1, 0]
    assert res["total_weight"] == 14

def test_multi_constraint_qubo_shape():
    """Verify QUBO dimensions with single and dual constraints."""
    vals = [10, 4, 7, 5, 8]
    wgts = [5, 3, 4, 2, 6]
    vols = [3, 4, 2, 1, 5]

    # Single constraint: 5 items + 4 slack = 9 qubits
    Q_single, off_single, info_single = build_multi_constraint_qubo(vals, wgts, max_weight=15)
    assert Q_single.shape == (9, 9)
    assert info_single["n_qubits"] == 9
    assert info_single["n_weight_slack"] == 4
    assert info_single["n_volume_slack"] == 0

    # Dual constraint: 5 items + 4 weight slack + 4 volume slack (10 L) = 13 qubits
    Q_dual, off_dual, info_dual = build_multi_constraint_qubo(
        vals, wgts, volumes=vols, max_weight=15, max_volume=10
    )
    assert Q_dual.shape == (13, 13)
    assert info_dual["n_qubits"] == 13
    assert info_dual["n_weight_slack"] == 4
    assert info_dual["n_volume_slack"] == 4

