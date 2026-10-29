"""Qiskit side: QAOA circuit, official transpilation, noise model, resource metrics, sampling.

Official settings (kit Section 3) are hard-coded below. Do NOT change them for required runs.
"""
from __future__ import annotations

from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap

from . import knapsack as K
from .processors import BASIS_GATES

SEED = 42            # seed_transpiler and seed_simulator
SHOTS = 4096
OPT_LEVEL = 1


# ----------------------------------------------------------------- circuit
def build_qaoa_circuit(gamma: float, beta: float, h, J, scale: float, n: int = K.N_QUBITS,
                       measure: bool = True) -> QuantumCircuit:
    """p = 1 QAOA for  C = sum h_i Z_i + sum J_ij Z_i Z_j  (both divided by `scale`).

        |+>^n  ->  exp(-i gamma C)  ->  exp(-i beta sum X)  ->  measure
    RZ(t) = exp(-i t Z / 2) and RZZ(t) = exp(-i t ZZ / 2), hence the factor 2.
    """
    qc = QuantumCircuit(n, name="QAOA_p1")
    qc.h(range(n))
    for i in range(n):
        if h[i] != 0:
            qc.rz(2 * gamma * h[i] / scale, i)
    for (i, j), v in J.items():
        qc.rzz(2 * gamma * v / scale, i, j)
    for i in range(n):
        qc.rx(2 * beta, i)
    if measure:
        qc.measure_all()
    return qc


# ----------------------------------------------------------------- hardware model
def coupling_map(proc: dict) -> CouplingMap:
    """Undirected edges: CX allowed in both directions."""
    pairs = []
    for a, b in proc["edges"]:
        pairs += [(a, b), (b, a)]
    return CouplingMap(couplinglist=pairs)


def build_noise_model(noise: dict):
    """Kit noise model: 1q depolarizing on rz/sx/x, 2q depolarizing on cx, symmetric readout flip."""
    from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error
    nm = NoiseModel(basis_gates=BASIS_GATES)
    nm.add_all_qubit_quantum_error(depolarizing_error(noise["p1"], 1), ["rz", "sx", "x"])
    nm.add_all_qubit_quantum_error(depolarizing_error(noise["p2"], 2), ["cx"])
    pr = noise["p_readout"]
    nm.add_all_qubit_readout_error(ReadoutError([[1 - pr, pr], [pr, 1 - pr]]))
    return nm


# ----------------------------------------------------------------- transpile + metrics
def transpile_official(qc: QuantumCircuit, proc: dict | None = None, extra_basis=()):
    """Official transpilation. proc=None -> no connectivity limit (used for logical CX)."""
    kw = dict(basis_gates=BASIS_GATES + list(extra_basis), optimization_level=OPT_LEVEL,
              seed_transpiler=SEED)
    if proc is not None:
        kw["coupling_map"] = coupling_map(proc)
    return transpile(qc, **kw)


def _depth(tqc, only_cx: bool = False) -> int:
    if only_cx:
        return tqc.depth(filter_function=lambda inst: inst.operation.name == "cx")
    return tqc.depth(filter_function=lambda inst: inst.operation.name not in ("measure", "barrier"))


def circuit_metrics(qc: QuantumCircuit, proc: dict) -> dict:
    """Kit Section 9 metrics, measured on the bound circuit with final measurements.

    swaps: the same routing is re-run with 'swap' kept as a basis gate, so the SWAPs inserted by
    the router are visible before they are decomposed into 3 CX. Cross-check this against the
    official circuit_metrics() in qff_phase2.py (see PROMPTS.md).
    """
    logical = transpile_official(qc, None)
    tqc = transpile_official(qc, proc)
    routed = transpile_official(qc, proc, extra_basis=["swap"])
    logical_cx = logical.count_ops().get("cx", 0)
    cx = tqc.count_ops().get("cx", 0)
    return dict(logical_qubits=qc.num_qubits, physical_qubits=proc["num_qubits"],
                logical_cx=logical_cx, cx=cx, cx_overhead=cx - logical_cx,
                depth=_depth(tqc), two_q_depth=_depth(tqc, only_cx=True),
                swaps=routed.count_ops().get("swap", 0))


def is_executable(qc: QuantumCircuit, proc: dict) -> bool:
    """Capacity rule: a circuit needing more qubits than the processor has is not run."""
    return qc.num_qubits <= proc["num_qubits"]


# ----------------------------------------------------------------- sampling
def run_counts(tqc: QuantumCircuit, noise: dict | None = None, shots: int = SHOTS) -> dict:
    """Sample a transpiled circuit on AerSimulator. noise=None -> ideal (same circuit, no noise)."""
    from qiskit_aer import AerSimulator
    kw = {}
    if noise is not None:
        kw["noise_model"] = build_noise_model(noise)
    sim = AerSimulator(**kw)
    result = sim.run(tqc, shots=shots, seed_simulator=SEED).result()
    return result.get_counts()


def sample(qc: QuantumCircuit, proc: dict, noisy: bool, shots: int = SHOTS):
    """Transpile for `proc`, sample, and return (counts, transpiled_circuit)."""
    tqc = transpile_official(qc, proc)
    counts = run_counts(tqc, proc["noise"] if noisy else None, shots)
    return counts, tqc


# ----------------------------------------------------------------- Constraint-Preserving Mixer circuit
def build_qaoa_cp_circuit(gamma, beta, h, J, scale, equal_pairs,
                           n=K.N_QUBITS, measure=True):
    """QAOA p=1 with a constraint-preserving XY mixer on equal-coefficient pairs.

    Instead of the standard RX(2*beta) on every qubit, this applies RXX+RYY
    on pairs of qubits whose constraint coefficients are equal.  Swapping
    equal-coefficient qubits preserves the linear constraint c^T y = W exactly,
    so the state stays in the feasible subspace.

    The initial state is a uniform superposition over feasible states, set
    via ``initialize`` (requires a statevector).  Use the helper in
    qaoa_numpy._feasible_initial_state().
    """
    from .qaoa_numpy import _feasible_initial_state
    import numpy as np
    psi0 = _feasible_initial_state()
    qc = QuantumCircuit(n, name="QAOA_CP_mixer")
    qc.initialize(psi0, range(n))
    # cost layer (same as standard QAOA)
    for i in range(n):
        if h[i] != 0:
            qc.rz(2 * gamma * h[i] / scale, i)
    for (i, j), v in J.items():
        qc.rzz(2 * gamma * v / scale, i, j)
    # constraint-preserving XY mixer
    for i, j in equal_pairs:
        qc.rxx(2 * beta, i, j)
        qc.ryy(2 * beta, i, j)
    if measure:
        qc.measure_all()
    return qc
