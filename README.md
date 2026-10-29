# QFF 2026 — Quantum Optimization — PS-O3: Resource-Constrained Item Selection (0/1 Knapsack)

**Team:** Emerging Genius  |  **Problem statement:** PS-O3 (only this one)  |  **Repo frozen at:** final commit before 5:40 PM IST, Day 2

## How to run (judges: follow exactly)
```bash
python3.11 -m venv .venv && source .venv/bin/activate     # Python 3.10-3.12
pip install -r requirements.txt
jupyter nbconvert --to notebook --execute main.ipynb --output main_executed.ipynb   # or open main.ipynb and Run All
```
Runtime: ~10-20 min on a laptop CPU (the 20x20 noisy landscape is reloaded from `results/landscape_D_noisy.npz`; set `RECOMPUTE = True` in the first cell to recompute it).
Quick formulation check without Qiskit: `python tests/check_formulation.py`.
`qff_phase2.py` (organiser starter module) is included unchanged.

## What the notebook does
1. Exact classical optimum by exhaustive search over 32 subsets → **V\* = 26** (items 1,2,3,4; weight 14).
2. QUBO: 5 item qubits + 4 binary slack qubits (weights 1,2,4,8), penalty **P = 5**; verified against the kit formula on all 512 bitstrings.
3. Ising Hamiltonian (36 ZZ terms), divided by its largest coefficient (120) — only rescales γ.
4. QAOA **p = 1**, seeds 0-4, γ,β ~ U[0,π], COBYLA (max 200 iterations), exact-statevector cost.
5. Processors A (5q, **not executable**: needs 9), B (9q) and D (our design), **ideal and noisy**, 4096 shots, official settings.
6. Resource table (logical CX, CX, depth, two-qubit depth, SWAPs, CX overhead), Bell-state study on D, 20x20 noisy objective landscape on D.

## Key results (fill from `results/tables/summary_for_readme.csv`)
| Processor | Condition | P_feasible (random 0.875) | P_opt (random 0.031) | Best feasible value (V\*=26) | Weight | % of optimal | CX | Depth | SWAPs |
|---|---|---|---|---|---|---|---|---|---|
| A | ideal / noisy | not executable: needs 9 qubits, has 5 | — | — | — | — | — | — | — |
| B | ideal | 0.9587 | 0.0210 | 26.0 | 14.0 | 100.0% | 121.0 | 117.0 | 17.0 |
| B | noisy | 0.9434 | 0.0249 | 26.0 | 14.0 | 100.0% | 121.0 | 117.0 | 17.0 |
| D | ideal | 0.9634 | 0.0225 | 26.0 | 14.0 | 100.0% | 102.0 | 87.0 | 10.0 |
| D | noisy | 0.9421 | 0.0225 | 26.0 | 14.0 | 100.0% | 102.0 | 87.0 | 10.0 |

## Repository layout
`main.ipynb` (run all) · `src/` (knapsack, QAOA, circuits, bell, landscape, design_d, results_io) · `processors/` (A, B, **D frozen**) ·
`data/instance.json` · `results/tables/{results.csv,bell.csv,...}` · `results/figures/` · `report.md` · `tests/check_formulation.py`

## Settings (official, unchanged for all required runs)
basis rz,sx,x,cx · `optimization_level=1`, SABRE (default), `seed_transpiler=42` · `AerSimulator`, `seed_simulator=42` · 4096 shots (landscape: 1024) ·
noise: 1q depolarizing 0.001 (rz,sx,x), 2q depolarizing 0.005 (cx), readout flip 0.01.

## Additional experiments (clearly labelled, not part of the required rows)
_List anything extra here, e.g. penalty sweep, unbalanced penalization, p = 2._

## AI tools used
Antigravity (Google DeepMind) was used for test automation, code verification, benchmark script authoring, and report drafting. All numerical results, QUBO formulations, and circuits were independently audited and verified against the official challenge kit.
