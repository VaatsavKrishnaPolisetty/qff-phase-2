"""Processor D design search (Objective 2).

Idea: the knapsack QUBO couples (almost) every qubit pair, 36 ZZ terms, but a processor may
have at most 4 neighbours per qubit. So routing (SWAPs) is the bottleneck. We generate many legal
topologies, transpile the SAME bound QAOA circuit on each with the official settings, and rank
them by CX count / depth / SWAPs. Compare against Processor B to quantify the improvement.
"""
from __future__ import annotations

import networkx as nx
import pandas as pd

from . import knapsack as K
from .circuits import circuit_metrics, sample
from .processors import PROCESSOR_B, BASIS_GATES, OFFICIAL_NOISE, candidate_graphs, make_processor_d, validate_processor_d


def search_topologies(qc, min_q: int = 9, max_q: int = 12, n_random: int = 6) -> pd.DataFrame:
    """Rank candidate graphs by routing cost for the bound QAOA circuit `qc` (with measurements)."""
    rows = []
    ref = circuit_metrics(qc, PROCESSOR_B)
    rows.append(dict(name="PROCESSOR_B (reference)", num_qubits=9, n_edges=len(PROCESSOR_B["edges"]),
                     max_degree=4, **ref))
    for name, (n, edges) in candidate_graphs(min_q, max_q, n_random).items():
        proc = make_processor_d(n, edges)
        ok, _ = validate_processor_d(proc, K.N_QUBITS)
        if not ok:
            continue
        g = nx.Graph(edges)
        m = circuit_metrics(qc, proc)
        rows.append(dict(name=name, num_qubits=n, n_edges=len(edges),
                         max_degree=max(dict(g.degree()).values()), **m))
    df = pd.DataFrame(rows)
    return df.sort_values(["cx", "depth", "swaps"]).reset_index(drop=True)


def quality_check(df: pd.DataFrame, qc, top_k: int = 5) -> pd.DataFrame:
    """Noisy sampling of the top-k topologies (quality can differ from CX count alone)."""
    cands = candidate_graphs()
    out = []
    for _, r in df.head(top_k + 1).iterrows():
        if r["name"].startswith("PROCESSOR_B"):
            proc = PROCESSOR_B
        else:
            n, edges = cands[r["name"]]
            proc = make_processor_d(n, edges)
        counts, _ = sample(qc, proc, noisy=True)
        ev = K.evaluate_counts(counts)
        out.append(dict(name=r["name"], cx=r["cx"], depth=r["depth"], swaps=r["swaps"],
                        p_feasible_noisy=ev["p_feasible"], p_opt_noisy=ev["p_opt"]))
    return pd.DataFrame(out)


def build_chosen(name: str, df: pd.DataFrame, team: str) -> dict:
    """Create the processor_D dict for the chosen candidate, with a rationale filled in from numbers."""
    n, edges = candidate_graphs()[name]
    row = df[df["name"] == name].iloc[0]
    ref = df[df["name"].str.startswith("PROCESSOR_B")].iloc[0]
    why = (f"Knapsack QUBO couples nearly all 9 qubits; on Processor B routing needs {int(ref['swaps'])} SWAPs "
           f"({int(ref['cx_overhead'])} extra CX, depth {int(ref['depth'])}). Topology '{name}' "
           f"({n} qubits, {len(edges)} edges, degree <= 4) cuts this to {int(row['swaps'])} SWAPs "
           f"({int(row['cx_overhead'])} extra CX, depth {int(row['depth'])}).")
    proc = make_processor_d(n, edges, team=team, rationale=why)
    ok, msgs = validate_processor_d(proc, K.N_QUBITS)
    assert ok, msgs
    return proc


# ----------------------------------------------------------------- Problem-Aware D (co-design)
def problem_aware_design(h: np.ndarray, J: dict, n_qubits: int = K.N_QUBITS,
                         max_degree: int = 4) -> list:
    """Design a topology that places the *strongest* ZZ couplings at graph distance 1.

    The knapsack Ising Hamiltonian has 36 ZZ terms of differing strength.
    Routing SWAPs are only needed for interactions at distance > 1, so placing
    the strongest couplings on direct edges minimises the gate-cost contribution
    of the most important terms.

    Algorithm:  (1) Build a minimum-weight spanning tree using the *strongest*
    edges (Kruskal with negated weights) to guarantee connectivity.
    (2) Greedily add remaining edges in descending |J_ij| order until every
    qubit reaches max_degree.
    """
    # All possible edges sorted by coupling strength (descending)
    all_edges = sorted(J.items(), key=lambda kv: abs(kv[1]), reverse=True)
    all_edges = [(min(i, j), max(i, j)) for (i, j), _ in all_edges]

    g = nx.Graph()
    g.add_nodes_from(range(n_qubits))
    degree = {i: 0 for i in range(n_qubits)}

    # Phase 1: Kruskal-style spanning tree (strongest edges first)
    for a, b in all_edges:
        if degree[a] >= max_degree or degree[b] >= max_degree:
            continue
        if not nx.has_path(g, a, b):
            g.add_edge(a, b)
            degree[a] += 1
            degree[b] += 1

    # Phase 2: fill remaining degree budget with strongest edges
    for a, b in all_edges:
        if degree[a] >= max_degree or degree[b] >= max_degree:
            continue
        if g.has_edge(a, b):
            continue
        g.add_edge(a, b)
        degree[a] += 1
        degree[b] += 1

    edges = sorted([sorted(e) for e in g.edges()])
    return edges


def problem_aware_processor(h: np.ndarray, J: dict, team: str = "Emerging Genius") -> dict:
    """Build a Processor D whose topology is co-designed with the knapsack Hamiltonian."""
    edges = problem_aware_design(h, J)
    n = len(edges[0]) if edges else K.N_QUBITS
    # num_qubits from max node index + 1
    n_qubits = max(max(a, b) for a, b in edges) + 1 if edges else K.N_QUBITS
    sorted_edges = sorted(set(tuple(sorted(e)) for e in edges))
    rationale = (
        f"Problem-aware co-design: 9-qubit topology with edges chosen to place the strongest "
        f"|J_ij| couplings at distance 1, minimising routing for the highest-weight ZZ terms. "
        f"{len(sorted_edges)} edges, max degree {max(dict(nx.Graph(sorted_edges).degree()).values())}."
    )
    proc = dict(name="Processor D (Problem-Aware)", team=team, problem_statement="PS-O3",
                num_qubits=n_qubits, edges=[list(map(int, e)) for e in sorted_edges],
                basis_gates=list(BASIS_GATES), noise=dict(OFFICIAL_NOISE),
                design_rationale=rationale)
    return proc
