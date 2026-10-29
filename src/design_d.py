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
from .processors import PROCESSOR_B, candidate_graphs, make_processor_d, validate_processor_d


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
