"""Processors A, B (fixed by the kit) and D (your design): load / validate / generate candidates.

Pure Python + networkx (no Qiskit needed).
NOTE: validate_processor_d() below mirrors kit rules 1-5. Before you freeze D, ALSO run the
official validate_processor_d() from qff_phase2.py - that one is what the judges use.
"""
from __future__ import annotations

import json
from pathlib import Path

import networkx as nx

BASIS_GATES = ["rz", "sx", "x", "cx"]
OFFICIAL_NOISE = dict(model="official", p1=0.001, p2=0.005, p_readout=0.01)

PROCESSOR_A = dict(name="Processor A", num_qubits=5,
                   edges=[[0, 1], [1, 2], [1, 3], [3, 4]],
                   basis_gates=BASIS_GATES, noise=dict(OFFICIAL_NOISE))
PROCESSOR_B = dict(name="Processor B", num_qubits=9,
                   edges=[[0, 1], [1, 2], [1, 6], [2, 3], [2, 6], [2, 5],
                          [3, 4], [4, 5], [5, 6], [6, 7], [6, 8], [8, 0]],
                   basis_gates=BASIS_GATES, noise=dict(OFFICIAL_NOISE))

PROC_DIR = Path(__file__).resolve().parent.parent / "processors"


def load_processor(path) -> dict:
    with open(path) as f:
        return json.load(f)


def save_processor(proc: dict, path) -> None:
    with open(path, "w") as f:
        json.dump(proc, f, indent=2)


def to_graph(proc: dict) -> nx.Graph:
    g = nx.Graph()
    g.add_nodes_from(range(proc["num_qubits"]))
    g.add_edges_from(map(tuple, proc["edges"]))
    return g


def validate_processor_d(proc: dict, required_qubits: int = 9):
    """Check kit rules 1-5. Returns (ok, list_of_messages)."""
    msgs, ok = [], True

    def fail(m):
        nonlocal ok
        ok = False
        msgs.append("FAIL: " + m)

    n = proc.get("num_qubits", 0)
    if not (required_qubits <= n <= 12):
        fail(f"rule 1: num_qubits={n} must be between {required_qubits} and 12")
    edges = [tuple(sorted(e)) for e in proc.get("edges", [])]
    if len(set(edges)) != len(edges):
        fail("duplicate edges")
    if any(a == b or not (0 <= a < n and 0 <= b < n) for a, b in edges):
        fail("an edge is a self-loop or uses a qubit index outside 0..num_qubits-1")
    g = to_graph(proc)
    if n and not nx.is_connected(g):
        fail("rule 2: graph is not connected")
    if n and max(dict(g.degree()).values()) > 4:
        fail(f"rule 3: max degree {max(dict(g.degree()).values())} > 4")
    if sorted(proc.get("basis_gates", [])) != sorted(BASIS_GATES):
        fail("rule 4: gate set must be exactly rz, sx, x, cx")
    noise = proc.get("noise", {})
    for key, official in (("p1", 0.001), ("p2", 0.005), ("p_readout", 0.01)):
        if noise.get(key, -1) < official:
            fail(f"rule 5: noise {key}={noise.get(key)} is better than official {official}")
    if ok:
        msgs.append("OK: rules 1-5 satisfied (own check; also run the official validator)")
    return ok, msgs


# ----------------------------------------------------------------- candidate topologies for D
def _edges(g: nx.Graph):
    return sorted([sorted(e) for e in g.edges()])


def candidate_graphs(min_q: int = 9, max_q: int = 12, n_random: int = 6) -> dict:
    """name -> (num_qubits, edges). Every candidate is connected with max degree <= 4."""
    cands = {}

    def add(name, g):
        g = nx.convert_node_labels_to_integers(g)
        if nx.is_connected(g) and max(dict(g.degree()).values()) <= 4 and min_q <= g.number_of_nodes() <= max_q:
            cands[name] = (g.number_of_nodes(), _edges(g))

    for n in range(min_q, max_q + 1):
        add(f"ring_n{n}", nx.cycle_graph(n))
        for offs in ([1, 2], [1, 3], [1, 4], [2, 3]):
            if max(offs) < n / 2:                      # keeps degree exactly 4
                add(f"circulant_n{n}_o{'-'.join(map(str, offs))}", nx.circulant_graph(n, offs))
        for s in range(n_random):
            add(f"rand4reg_n{n}_s{s}", nx.random_regular_graph(4, n, seed=s))
    add("grid_3x3", nx.grid_2d_graph(3, 3))
    add("grid_2x5", nx.grid_2d_graph(2, 5))
    add("grid_3x4", nx.grid_2d_graph(3, 4))
    return cands


def make_processor_d(num_qubits, edges, team="YOUR_TEAM_NAME", rationale="") -> dict:
    return dict(name="Processor D", team=team, problem_statement="PS-O3",
                num_qubits=int(num_qubits), edges=[list(map(int, e)) for e in edges],
                basis_gates=list(BASIS_GATES), noise=dict(OFFICIAL_NOISE),
                design_rationale=rationale)
