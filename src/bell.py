"""Objective 1: Bell state |Phi+> on Processor D, XX / YY / ZZ correlations and fidelity.

F = (1 + <XX> - <YY> + <ZZ>) / 4   (NOT P(00)+P(11); that scores 0 for correctness).
Your numbers must agree with the starter pack's bell_experiment() within 2 standard errors.
"""
from __future__ import annotations

import itertools
import math

import networkx as nx
from qiskit import QuantumCircuit, transpile

from .circuits import BASIS_GATES, OPT_LEVEL, SEED, SHOTS, coupling_map, run_counts
from .processors import to_graph


def bell_circuit(basis: str) -> QuantumCircuit:
    """H on q0, CX(0->1), then basis change on both qubits, then measure."""
    qc = QuantumCircuit(2, 2, name=f"bell_{basis}")
    qc.h(0)
    qc.cx(0, 1)
    if basis == "XX":
        qc.h(0)
        qc.h(1)
    elif basis == "YY":
        qc.sdg(0)
        qc.sdg(1)
        qc.h(0)
        qc.h(1)
    elif basis != "ZZ":
        raise ValueError(basis)
    qc.measure([0, 1], [0, 1])
    return qc


def correlation(counts: dict) -> tuple[float, float]:
    """<P> = (N_even - N_odd)/N  and  SE = sqrt((1 - <P>^2)/N)."""
    n = sum(counts.values())
    even = counts.get("00", 0) + counts.get("11", 0)
    p = (even - (n - even)) / n
    return p, math.sqrt(max(0.0, 1 - p * p) / n)


def adjacent_pair(proc: dict) -> tuple[tuple[int, int], int]:
    a, b = sorted(map(tuple, (sorted(e) for e in proc["edges"])))[0]
    return (a, b), 1


def farthest_pair(proc: dict) -> tuple[tuple[int, int], int]:
    g = to_graph(proc)
    dist = dict(nx.all_pairs_shortest_path_length(g))
    best = max(itertools.combinations(sorted(g.nodes), 2), key=lambda ab: (dist[ab[0]][ab[1]], -ab[0], -ab[1]))
    return best, dist[best[0]][best[1]]


def bell_experiment(proc: dict, pair: tuple[int, int], noisy: bool, shots: int = SHOTS) -> dict:
    """Run the 3 basis circuits on physical qubits `pair` of `proc`."""
    cm = coupling_map(proc)
    out = {}
    for basis in ("XX", "YY", "ZZ"):
        qc = bell_circuit(basis)
        tqc = transpile(qc, basis_gates=BASIS_GATES, coupling_map=cm, initial_layout=list(pair),
                        optimization_level=OPT_LEVEL, seed_transpiler=SEED)
        counts = run_counts(tqc, proc["noise"] if noisy else None, shots)
        out[basis] = correlation(counts)
        if basis == "ZZ":
            out["cx_count"] = tqc.count_ops().get("cx", 0)
    (xx, sxx), (yy, syy), (zz, szz) = out["XX"], out["YY"], out["ZZ"]
    fid = (1 + xx - yy + zz) / 4
    fid_se = 0.25 * math.sqrt(sxx ** 2 + syy ** 2 + szz ** 2)
    return dict(pair=f"{pair[0]}-{pair[1]}", condition="noisy" if noisy else "ideal",
                cx_count=out["cx_count"], XX=xx, XX_se=sxx, YY=yy, YY_se=syy,
                ZZ=zz, ZZ_se=szz, F=fid, F_se=fid_se)


def run_all(proc: dict) -> list[dict]:
    """2 pairs x 2 conditions x 3 bases = 12 circuits. Returns the rows of bell.csv."""
    rows = []
    for label, (pair, dist) in (("adjacent", adjacent_pair(proc)), ("farthest", farthest_pair(proc))):
        for noisy in (False, True):
            r = bell_experiment(proc, pair, noisy)
            r.update(pair_type=label, distance=dist)
            rows.append(r)
    return rows
