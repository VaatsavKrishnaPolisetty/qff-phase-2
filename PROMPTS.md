# Prompts for Antigravity IDE (copy-paste, in order)

**Before the first prompt**
1. Unzip this project into your QFF folder (e.g. `~/QFF/qff_ps_o3`) and open that folder in Antigravity.
2. Copy the organisers' starter-pack files into the project root: `qff_phase2.py`, `instances.json`, `processor_D_template.json`, `example_usage.py`.
3. Select the interpreter `~/QFF/.qff2026-venv/bin/python` (the one your install script created).
4. In the terminal: `python tests/check_formulation.py`. It must print `ALL FORMULATION CHECKS PASSED`.

---

## PROMPT 0: context (paste this first, once)
```
You are helping me finish a hackathon project: QFF 2026 Phase 2, Quantum Optimization track, problem PS-O3 (0/1 knapsack with QAOA).
Read these files first: README.md, main.ipynb, everything in src/, tests/check_formulation.py, and the starter-pack files qff_phase2.py, example_usage.py, instances.json.

HARD RULES
- NEVER edit qff_phase2.py (organiser file) and never change the locked instance or the official settings for required runs:
  basis rz,sx,x,cx; optimization_level=1; SABRE default; seed_transpiler=42; AerSimulator seed_simulator=42; 4096 shots
  (landscape 1024); noise = 1q depolarizing 0.001 on rz/sx/x, 2q depolarizing 0.005 on cx, symmetric readout flip 0.01.
- Required encoding: 5 item qubits + 4 slack qubits (weights 1,2,4,8), penalty P=5, QAOA p=1, seeds 0-4, gamma,beta ~ U[0,pi].
- Feasibility is judged on the 5 item bits only. Processor A (5 qubits) is "not executable: needs 9 qubits, has 5".
- Anything beyond the required runs must be labelled "additional experiment".
- Do not invent numbers. Every number in the report/README must come from files in results/ produced by main.ipynb.
Confirm you understood, then wait for my next prompt.
```

## PROMPT 1: first run and debugging (the Qiskit parts were not executed when written)
```
Run `python tests/check_formulation.py`, then execute main.ipynb top to bottom (e.g. `jupyter nbconvert --to notebook --execute main.ipynb --output main_executed.ipynb`).
Fix any error in src/ or the notebook with the smallest possible change (likely candidates: Qiskit/Aer API differences in src/circuits.py, src/bell.py, src/landscape.py).
Do NOT change official settings or the formulation. After it runs end-to-end, tell me: runtime, the qiskit and qiskit-aer versions, and the contents of results/tables/results.csv.
```

## PROMPT 2: cross-check against the organiser starter pack (protects C1, C3, C4 points)
```
Compare my implementation with the organiser functions in qff_phase2.py and example_usage.py WITHOUT editing qff_phase2.py:
1. counts_to_x(): confirm my bit order (int(key,2), qubit i = bit i) gives the same item bits.
2. circuit_metrics(circuit, processor): run it on my bound QAOA circuit for Processors B and D and compare logical_cx, cx, depth, two_q_depth, swaps, cx_overhead with src/circuits.py::circuit_metrics. If they differ, make my numbers match the official definition (use the official function inside my code if possible).
3. bell_experiment(processor, physical_pair, noisy): compare with src/bell.py for the same pairs; XX, YY, ZZ and F must agree within 2 standard errors.
4. The official noise model: check that src/circuits.py::build_noise_model is equivalent.
5. validate_processor_d(D, 9) on processors/processor_D.json.
6. Check example_usage.py for how results.csv is written for PS-O3: which metric goes in quality_metric/quality_value (P_feasible? % of optimal value?), then adapt src/results_io.py so results.csv matches exactly.
7. Compare data/instance.json with the PS-O3 entry of instances.json; replace mine with the official copy if different.
Report every discrepancy in a table and fix them.
```

## PROMPT 3: design and freeze Processor D (20 points)
```
Set RUN_D_SEARCH = True in main.ipynb and run the D-search cells. It ranks all legal topologies (connected, max degree 4, 9-12 qubits) by CX, depth and SWAPs against Processor B and checks noisy quality for the top candidates.
1. Show me the top 10 (results/tables/d_search.csv, d_search_quality.csv) and the bottleneck numbers on Processor B (SWAPs, CX overhead, depth).
2. Recommend ONE topology, balancing routing cost, noisy P_feasible/P_opt, and qubit count. Explain the choice in 3 sentences.
3. After I confirm, set CHOSEN_D to its name, run the cell to write processors/processor_D.json, validate it with BOTH my validator and the official validate_processor_d, then set CHOSEN_D = None and RUN_D_SEARCH = False. From then on D is FROZEN: never modify processor_D.json again.
4. Write results/figures/processor_D_graph.png (a clear drawing of D) and a short text for the report: bottleneck seen on B (with numbers), expected effect of D, measured effect on D (from results.csv), and ONE honest trade-off (e.g. degree-4 qubits mean more crosstalk risk on real hardware).
```

## PROMPT 4: Bell-state interpretation (C1)
```
Using results/tables/bell.csv write 3-5 sentences for the report explaining (a) why the noisy fidelity is lower than the ideal one and (b) why the farthest pair is worse than the adjacent pair (routing SWAPs, extra CX gates, readout error). Quote the actual numbers (F with standard errors, CX counts). Check that ideal XX and ZZ are about +1 and YY about -1, and that F is computed as (1 + XX - YY + ZZ)/4.
```

## PROMPT 5: results analysis (C5, 20 points)
```
From results/tables/results.csv, results_detail.csv, qaoa_seeds.csv and the landscape figure, write the analysis section of the report. Answer with numbers only taken from those files:
1. Did QAOA beat uniform random on P_feasible (0.875) and on P_opt (0.031), on B and D, ideal and noisy? If not, say so plainly.
2. Why does minimising the average QUBO cost raise feasibility but not necessarily the probability of the single optimal subset? Why does "best feasible value" saturate at 100% for any sampler with 4096 shots?
3. Connectivity: B vs D in SWAPs, CX count, depth, and the effect on noisy results. Is D more efficient than B at equal quality?
4. Landscape interpretation: location of the optimum, narrowness of the good region, how noise flattens it (noisy vs ideal panel), why seeds 0, 2, 4 got stuck in poor local minima.
5. Limitations (p=1, 9 qubits, dense QUBO on degree-limited hardware, slack-qubit overhead, simulator noise only) and 3 concrete evidence-based next steps.
```

## PROMPT 6: final report (about 4-8 pages) and README
```
Create report.md (4-8 pages) with these sections: 1 Problem and formulation (QUBO matrix, Ising, scaling), 2 Bell-state results, 3 Processor D design and justification (drawing, bottleneck numbers, expected vs measured effect, trade-off), 4 Results on A/B/D ideal and noisy vs classical optimum and random baseline (tables from results/), 5 Landscape, 6 Trade-offs, limitations, improvements. Embed figures from results/figures/. Then fill in the README results table from results/tables/summary_for_readme.csv. Leave the AI-tools section for me to complete. Use only numbers present in results/; list any number you are unsure about.
```

## PROMPT 7: reproducibility test (C4, 15 points: first-attempt success = 6 points)
```
Simulate a judge: in a temporary folder, `git clone` this repository (after I commit), create a fresh virtual environment with Python 3.11, `pip install -r requirements.txt`, and execute main.ipynb from top to bottom with no edits. Measure the runtime (must be under 30 minutes). Compare the numbers in the fresh results/tables/results.csv and bell.csv with the committed ones; they must match exactly (seeds are fixed). Also verify: requirements.txt has exact pinned versions of what was used (replace the ranges using pip freeze), every seed is visible in the notebook, results.csv uses the exact kit column format, and a Processor B result is produced (gate G3). Report any failure and fix it.
```

## PROMPT 8: optional extras (clearly labelled "additional experiment"; do only if time is left)
```
Add a separate notebook section titled "Additional experiments" (never changing the required rows) with ONE or TWO of:
(a) Penalty sweep P in {2, 5, 10, 20} on Processor D noisy: P_feasible, P_opt, QUBO-minimum validity.
(b) Unbalanced penalisation (no slack qubits, 5 qubits): this fits Processor A, answering the capacity limit. Show A/B/D results and compare resources.
(c) p = 2 QAOA as a separate row.
(d) Coarse (gamma, beta) grid-search initialisation versus the 5 random seeds.
Save outputs to results/extra/ and discuss honestly whether they help.
```

## PROMPT 9: final audit before the 5:40 PM IST freeze
```
Audit the repository against this checklist and report PASS/FAIL for each line with evidence:
G1 repo URL ready; G2 README names PS-O3 only; G3 main.ipynb runs from the README and produces Processor B results; G4 results/tables/results.csv and report.md exist.
C1 bell.csv has adjacent and farthest pair, ideal and noisy, F = (1+XX-YY+ZZ)/4 with SE.
C2 processor_D.json passes the official validate_processor_d; frozen (git log shows no changes after the final runs); drawing and trade-off in the report.
C3 9-qubit QUBO with 4 slack bits and P=5; feasibility on item bits only; exhaustive V*=26; A/B/D rows (A = not executable); landscape on D with the optimum marked; resource table; random baseline 0.875.
C4 numbers in report == numbers produced by the notebook; pinned requirements; seeds visible; runtime < 30 min.
C5 report discusses connectivity vs SWAPs/depth/noisy results, landscape, limitations and next steps.
Deductions: any missing required run (-2 each); any change to the locked instance or official settings.
```
