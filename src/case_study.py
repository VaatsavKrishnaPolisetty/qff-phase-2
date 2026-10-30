"""Disaster-Relief Cargo Optimization & Multi-Constraint QUBO Generalization.

Real-World Case Study:
Emergency aerial humanitarian relief loading for disaster zones (floods, earthquakes).
Payload capacity is tightly constrained by drone/helicopter lift limits and cargo bay volume.

Items:
1. Trauma & Surgical Medical Kits (v=10, w=5 kg, vol=3 L)
2. Water Filtration & Purification Units (v=4, w=3 kg, vol=4 L)
3. Emergency High-Calorie Rations (v=7, w=4 kg, vol=2 L)
4. Satellite Communications & GPS Beacon (v=5, w=2 kg, vol=1 L)
5. Portable Micro-Generator & Power Station (v=8, w=6 kg, vol=5 L)

Provides:
- build_multi_constraint_qubo(): Generalized QUBO generator supporting arbitrary item lists
  and dual constraints (Weight + Volume) via log-binary slack qubit expansions.
- analyze_qubit_scaling(): Comprehensive scaling analysis O(N + log W + log V).
"""

from pathlib import Path
import math
import numpy as np
import pandas as pd

# Real-world disaster relief item registry
DISASTER_RELIEF_ITEMS = [
    {"id": 1, "name": "Trauma & Surgical Medical Kits", "value": 10, "weight": 5, "volume": 3},
    {"id": 2, "name": "Water Purification & Filtration Units", "value": 4, "weight": 3, "volume": 4},
    {"id": 3, "name": "Emergency High-Calorie Rations", "value": 7, "weight": 4, "volume": 2},
    {"id": 4, "name": "Satellite Comms & Emergency Beacon", "value": 5, "weight": 2, "volume": 1},
    {"id": 5, "name": "Portable Micro-Generator & Batteries", "value": 8, "weight": 6, "volume": 5},
]

def num_slack_bits(capacity: int) -> int:
    """Number of binary slack bits required to represent values 0..capacity."""
    if capacity <= 0:
        return 0
    return math.floor(math.log2(capacity)) + 1

def build_multi_constraint_qubo(
    values: list,
    weights: list,
    volumes: list = None,
    max_weight: int = 15,
    max_volume: int = None,
    penalty_weight: float = 5.0,
    penalty_volume: float = 5.0,
):
    """Generalised QUBO builder supporting arbitrary items and dual (weight + volume) constraints.

    Variables order:
      x_0 .. x_{N-1}            : item decision binary variables
      s_0^(w) .. s_{K_w-1}^(w)  : weight slack binary variables (weights 2^k)
      s_0^(v) .. s_{K_v-1}^(v)  : volume slack binary variables (weights 2^k, if volume specified)

    Returns:
      Q: (n_qubits, n_qubits) upper-triangular QUBO matrix
      offset: constant scalar energy term
      info: dictionary with qubit allocations and metadata
    """
    n_items = len(values)
    k_w = num_slack_bits(max_weight)
    k_v = num_slack_bits(max_volume) if (max_volume is not None and volumes is not None) else 0
    n_total = n_items + k_w + k_v

    Q = np.zeros((n_total, n_total), dtype=float)
    offset = 0.0

    # 1. Objective: Maximize sum(values * x) -> Minimize -sum(values * x)
    for i in range(n_items):
        Q[i, i] -= float(values[i])

    # 2. Weight constraint: P_w * (sum(w_i x_i) + sum(2^k s_k^w) - W)^2
    # Expanding (Linear + Slack - W)^2 = (Linear + Slack)^2 - 2W(Linear + Slack) + W^2
    w_coeffs = np.zeros(n_total, dtype=float)
    for i in range(n_items):
        w_coeffs[i] = float(weights[i])
    for k in range(k_w):
        w_coeffs[n_items + k] = float(1 << k)

    # Add P_w * [ w_coeffs.T @ w_coeffs ]
    for i in range(n_total):
        for j in range(i, n_total):
            coeff = w_coeffs[i] * w_coeffs[j]
            if coeff != 0:
                if i == j:
                    # x_i^2 = x_i for binary variables
                    Q[i, i] += penalty_weight * (coeff - 2.0 * max_weight * w_coeffs[i])
                else:
                    Q[i, j] += penalty_weight * 2.0 * coeff
    offset += penalty_weight * (max_weight ** 2)

    # 3. Optional Volume constraint: P_v * (sum(v_i x_i) + sum(2^k s_k^v) - V)^2
    if k_v > 0 and volumes is not None:
        v_coeffs = np.zeros(n_total, dtype=float)
        for i in range(n_items):
            v_coeffs[i] = float(volumes[i])
        for k in range(k_v):
            v_coeffs[n_items + k_w + k] = float(1 << k)

        for i in range(n_total):
            for j in range(i, n_total):
                coeff = v_coeffs[i] * v_coeffs[j]
                if coeff != 0:
                    if i == j:
                        Q[i, i] += penalty_volume * (coeff - 2.0 * max_volume * v_coeffs[i])
                    else:
                        Q[i, j] += penalty_volume * 2.0 * coeff
        offset += penalty_volume * (max_volume ** 2)

    info = {
        "n_items": n_items,
        "n_weight_slack": k_w,
        "n_volume_slack": k_v,
        "n_qubits": n_total,
        "max_weight": max_weight,
        "max_volume": max_volume,
        "penalty_weight": penalty_weight,
        "penalty_volume": penalty_volume,
    }
    return Q, offset, info

def solve_case_study_brute_force(values, weights, volumes=None, max_weight=15, max_volume=None):
    """Exhaustive search over item space to find ground-truth optimal feasible cargo."""
    n_items = len(values)
    best_val = -1
    best_combo = None
    best_weight = 0
    best_volume = 0

    for state in range(1 << n_items):
        bits = [(state >> i) & 1 for i in range(n_items)]
        w_sum = sum(b * weights[i] for i, b in enumerate(bits))
        v_sum = sum(b * volumes[i] for i, b in enumerate(bits)) if volumes else 0
        val = sum(b * values[i] for i, b in enumerate(bits))

        is_feasible = (w_sum <= max_weight)
        if volumes and max_volume is not None:
            is_feasible = is_feasible and (v_sum <= max_volume)

        if is_feasible and val > best_val:
            best_val = val
            best_combo = bits
            best_weight = w_sum
            best_volume = v_sum

    return {
        "best_selection": best_combo,
        "best_value": best_val,
        "total_weight": best_weight,
        "total_volume": best_volume,
    }

def analyze_qubit_scaling(output_csv: Path = None):
    """Calculates scaling of required qubit register across problem dimensions."""
    if output_csv is None:
        output_csv = Path(__file__).resolve().parent.parent / "results/extra/case_study_scaling.csv"
    records = []
    item_sizes = [5, 10, 20, 50, 100]
    weight_capacities = [15, 30, 60, 120, 250, 500]
    volume_capacities = [10, 20, 40, 80, 150, 300]

    for n in item_sizes:
        for w, v in zip(weight_capacities, volume_capacities):
            k_w = num_slack_bits(w)
            k_v = num_slack_bits(v)
            qubits_single = n + k_w
            qubits_dual = n + k_w + k_v
            records.append({
                "num_items": n,
                "weight_capacity_kg": w,
                "volume_capacity_L": v,
                "slack_weight_bits": k_w,
                "slack_volume_bits": k_v,
                "total_qubits_single_constraint": qubits_single,
                "total_qubits_dual_constraint": qubits_dual,
                "qubit_scaling_ratio_dual_to_items": round(qubits_dual / n, 2),
            })

    df = pd.DataFrame(records)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"Saved qubit scaling analysis to {output_csv}")
    return df



def get_all_mission_case_studies():
    """Returns the 5 canonical real-world mission domains mapped to PS-O3."""
    json_path = Path(__file__).resolve().parent.parent / "data/mission_case_studies.json"
    if json_path.exists():
        import json
        with open(json_path) as f:
            return json.load(f)
    return [
        {
            "id": "disaster_relief",
            "title": "Autonomous Drone Emergency Disaster-Relief Cargo Loading",
            "domain": "Humanitarian Aerospace Logistics",
            "max_weight": 15, "weight_unit": "kg",
            "max_volume": 10, "volume_unit": "L",
            "items": DISASTER_RELIEF_ITEMS
        }
    ]

if __name__ == "__main__":
    # 1. Official 5-item Disaster Relief validation
    vals = [item["value"] for item in DISASTER_RELIEF_ITEMS]
    wgts = [item["weight"] for item in DISASTER_RELIEF_ITEMS]
    vols = [item["volume"] for item in DISASTER_RELIEF_ITEMS]

    res_single = solve_case_study_brute_force(vals, wgts, max_weight=15)
    print("Disaster Relief (Weight Only, W=15 kg):")
    print(f"  Optimal Cargo Value: {res_single['best_value']}")
    print(f"  Selected Items: {res_single['best_selection']} (Weight: {res_single['total_weight']} kg)")

    res_dual = solve_case_study_brute_force(vals, wgts, volumes=vols, max_weight=15, max_volume=10)
    print("Disaster Relief (Dual Constraint: W=15 kg, V=10 L):")
    print(f"  Optimal Cargo Value: {res_dual['best_value']}")
    print(f"  Selected Items: {res_dual['best_selection']} (Weight: {res_dual['total_weight']} kg, Volume: {res_dual['total_volume']} L)")

    # 2. Qubit scaling table
    df_scaling = analyze_qubit_scaling()
    print("\nScaling table head:")
    print(df_scaling.head(10).to_string())

