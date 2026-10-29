"""results.csv in the exact kit column format (+ results_detail.csv with every metric)."""
from __future__ import annotations

import csv
from pathlib import Path

from . import knapsack as K

KIT_COLUMNS = ["problem_id", "processor", "condition", "executable", "logical_qubits", "physical_qubits",
               "logical_cx", "cx", "depth", "two_q_depth", "swaps", "cx_overhead", "shots",
               "quality_metric", "quality_value", "p_opt", "classical_optimum", "random_baseline"]

PROBLEM_ID = "PS-O3"


def not_executable_row(proc_name: str, condition: str, physical_qubits: int) -> dict:
    return dict(problem_id=PROBLEM_ID, processor=proc_name, condition=condition, executable="false",
                logical_qubits=K.N_QUBITS, physical_qubits=physical_qubits)


def result_row(proc_name: str, condition: str, metrics: dict, ev: dict, shots: int) -> dict:
    """quality_metric = p_feasible (random baseline 0.875). % of optimal value and the rest are in
    results_detail.csv. (Check example_usage.py of the starter pack for the expected PS-O3 metric.)"""
    base = K.random_baseline()
    return dict(problem_id=PROBLEM_ID, processor=proc_name, condition=condition, executable="true",
                logical_qubits=metrics["logical_qubits"], physical_qubits=metrics["physical_qubits"],
                logical_cx=metrics["logical_cx"], cx=metrics["cx"], depth=metrics["depth"],
                two_q_depth=metrics["two_q_depth"], swaps=metrics["swaps"],
                cx_overhead=metrics["cx_overhead"], shots=shots,
                quality_metric="p_feasible", quality_value=round(ev["p_feasible"], 6),
                p_opt=round(ev["p_opt"], 6), classical_optimum=K.V_STAR,
                random_baseline=base["p_feasible"])


def write_results_csv(rows: list[dict], path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=KIT_COLUMNS, restval="")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in KIT_COLUMNS})


def write_detail_csv(rows: list[dict], path) -> None:
    path = Path(path)
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, restval="")
        w.writeheader()
        w.writerows(rows)
