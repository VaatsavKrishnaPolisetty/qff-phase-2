# QFF 2026 — Quantum Optimization — PS-O3: Resource-Constrained Item Selection (0/1 Knapsack)

**Team:** Emerging Genius  |  **Problem statement:** PS-O3 (only this one)  |  **Repo frozen at:** final commit before 5:40 PM IST, Day 2

## How to run (judges: follow exactly)
```bash
python3.11 -m venv .venv && source .venv/bin/activate     # Python 3.10-3.12
pip install -r requirements.txt
pytest tests/ -v                                         # Automated test suite (16 tests)
python tests/check_formulation.py                        # Fast formulation self-check (<0.2s)
jupyter nbconvert --to notebook --execute main.ipynb --output main_executed.ipynb   # or open main.ipynb and Run All
```
Runtime: ~10-20 min on a laptop CPU (the 20x20 noisy landscape is reloaded from `results/landscape_D_noisy.npz`; set `RECOMPUTE = True` in the first cell to recompute it).
`qff_phase2.py` (organiser starter module) is included unchanged. Automated CI executes on every push via `.github/workflows/ci.yml`.

## Interactive Frontend & Evaluation Hub (Judges Review)
Launch our interactive visual evaluation web application:
```bash
./run_frontend.sh        # or: python3 run_frontend.py
```
Opens `http://localhost:8080` in your browser:
- **🎯 Guided Judge Walkthrough (Driver.js):** Interactive tour taking you through all 8 key project milestones.
- **⚡ Interactive QAOA Playground:** Toggle item combinations, observe the 4 binary slack qubits in real-time, and verify QUBO energy calculations.
- **🔬 Hardware & Pareto Explorer:** Visualizes our 48-topology Pareto frontier and coupling graphs (Processor A vs B vs D).
- **📁 File Inspector (51 Files):** Complete interactive repository browser with syntax highlighting for all scripts, datasets, and reports.
- **🎤 3-Minute Pitch Teleprompter:** Live timer, slide visual cues, and presentation script.
- **⚖️ Rubric Compliance Matrix:** 100% PASS verification checklist (G1–G4, C1–C5).

To regenerate `report.pdf` from `report.md`:
```bash
pandoc report.md -o report.pdf --pdf-engine=xelatex -V geometry:margin=1in
```
(requires pandoc and a LaTeX engine; `report.html` is also available as an alternative format.)

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

## Additional experiments & engineering deliverables (clearly labelled, not part of the required rows)
1. **Design Pareto Trade-Off Analysis**: 48 candidate topologies (degree-2 rings, degree-3 grids, 10-12Q variants) plotted as CX vs. edges (chip cost proxy) in `results/figures/pareto_design_d.png`.
2. **Disaster-Relief Case Study & Multi-Constraint Scaling**: Emergency aerial relief cargo loading and generalized QUBO ($N + \log W + \log V$) in `src/case_study.py` and `results/extra/case_study_scaling.csv`.
3. **Automated CI & Unit Testing**: Full 16-test suite in `tests/` and automated GitHub Actions workflow in `.github/workflows/ci.yml`.
4. **Penalty sweep** (P ∈ {2, 5, 10, 20} on Processor D, noisy): QUBO-minimum validity, P_feasible, P_opt.
5. **Shifted-target quadratic penalty** (5 qubits, no slack): eliminates slack overhead, fits Processor A. A/B/D resources and results.
6. **Depth p = 2 QAOA**: second variational layer on Processor D.
7. **Zero-Noise Extrapolation** (digital unitary folding, λ ∈ {1, 3, 5}): extrapolate to zero-noise mean QUBO cost.
8. **Warm-started QAOA** (LP relaxation): continuous relaxation → RY initial state + tilted mixer.
9. **Realistic IBM hardware noise** (GenericBackendV2): non-uniform T1/T2, calibrated CX durations.
10. **OpenQASM 3.0 export & pulse-timing analysis**: production-ready circuit export, nanosecond latency budget.
11. **Conditional Value-at-Risk (CVaR) QAOA** (α ∈ {0.05, 0.1, 0.2, 0.3}): tail-focused cost function to boost P_opt.
12. **Measurement Error Mitigation**: pseudo-inverse of the 2^9 readout bit-flip channel applied to noisy counts.
13. **Problem-Aware Processor D** (architecture-algorithm co-design): topology placing the strongest ZZ couplings at distance 1.
14. **Constraint-Preserving Mixer QAOA**: XY mixer on equal-coefficient qubit pairs preserves the linear constraint, guaranteeing 100% feasibility.

## AI tools used
Antigravity (Google DeepMind) was used for test automation, code verification, benchmark script authoring, and report drafting. All numerical results, QUBO formulations, and circuits were independently audited and verified against the official challenge kit.
