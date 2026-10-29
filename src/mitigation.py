"""Measurement Error Mitigation (MEM).

The official noise model applies a symmetric bit-flip readout error with
probability p_readout = 0.01 per measured qubit.  This means the *observed*
counts distribution is the *true* distribution convolved with the readout
channel:

    observed = M @ true

where M is the 2^n × 2^n transition matrix (Kronecker product of n single-qubit
bit-flip matrices).  Mitigation solves the linear system for `true`:

    true = M^{-1} @ observed   (via least-squares for numerical stability).

After solving, negative probabilities are clipped to zero and the vector is
renormalised back to the original shot count.
"""
from __future__ import annotations

import numpy as np


def build_readout_matrix(n_qubits: int, p_readout: float) -> np.ndarray:
    """2^n × 2^n readout transition matrix for symmetric bit-flip noise.

    M[b, b'] = P(observe b' | actual b).  Built as the n-fold Kronecker product
    of the single-qubit matrix [[1-p, p], [p, 1-p]].
    """
    single = np.array([[1 - p_readout, p_readout],
                       [p_readout, 1 - p_readout]])
    M = single.copy()
    for _ in range(n_qubits - 1):
        M = np.kron(M, single)
    return M


def counts_to_vec(counts: dict, n_qubits: int) -> np.ndarray:
    """Convert a Qiskit counts dict to a length-2^n probability vector."""
    vec = np.zeros(1 << n_qubits)
    total = sum(counts.values())
    for key, c in counts.items():
        b = int(key.replace(" ", ""), 2)
        vec[b] = c / total
    return vec


def mitigate_counts(counts: dict, n_qubits: int, p_readout: float = 0.01) -> dict:
    """Apply measurement error mitigation via least-squares matrix inversion.

    Returns a new counts dict (integer counts, same total as input).
    """
    total = int(sum(counts.values()))
    observed = counts_to_vec(counts, n_qubits)
    M = build_readout_matrix(n_qubits, p_readout)
    # Solve M @ true = observed  (M is invertible for p_readout < 0.5)
    true, _, _, _ = np.linalg.lstsq(M, observed, rcond=None)
    # Clip negatives, renormalise to original shot count
    true = np.maximum(true, 0)
    s = true.sum()
    if s > 0:
        true = true / s * total
    # Convert back to integer counts, keeping only non-negligible entries
    mitigated = {}
    for b in range(1 << n_qubits):
        if true[b] > 0.5:
            key = format(b, f"0{n_qubits}b")
            mitigated[key] = int(round(true[b]))
    return mitigated
