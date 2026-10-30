# Evaluator & Contributor Guide

**Team:** Emerging Genius  
**Problem Statement:** PS-O3 (0/1 Knapsack Problem with QAOA)  
**Hackathon:** Qiskit Fall Fest (QFF) 2026 Phase 2  

This repository contains the complete, reproducible Phase 2 quantum optimization pipeline, theoretical derivations, hardware topology co-design benchmarks, and interactive evaluation frontend.

---

## 🚀 Quick Reproduction Guide

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/VaatsavKrishnaPolisetty/qff-phase-2.git
cd qff-phase-2

# Create and activate a clean virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install exact pinned dependencies
pip install -r requirements.txt
```

### 2. Verify Mathematical Formulation
Run the exhaustive formulation verification check:
```bash
python tests/check_formulation.py
```
*Expected Output:*
- Ground truth optimal subset: Items `{1, 2, 3, 4}` with $V^* = 26$, total weight $14 \le 15$.
- Feasible state ratio: $28 / 32 = 87.50\%$.
- QUBO minimum eigenvalue: $-26.0$ with zero violations.

### 3. Run Automated Pytest Suite
Run the full 16-test suite verifying processors, Bell fidelities, QUBO symmetry, and Pareto optimality:
```bash
pytest tests/ -v
```

### 4. Run End-to-End Pipeline in Jupyter Notebook
Launch the locked evaluation notebook:
```bash
jupyter notebook main.ipynb
```
Execute cells top-to-bottom to reproduce the experimental benchmarks across Processors A, B, and D.

### 5. Launch the Interactive Frontend Evaluation Hub
To explore the interactive 7-tab dashboard locally (Knapsack simulator, Pareto plot, horizontal figure study dossiers, 51-file code inspector, rubric audit, and pitch teleprompter):
```bash
python run_frontend.py
```
Then navigate to `http://localhost:8080` in your web browser.

---

## 📁 Repository Structure

- `src/` — Modular, production-grade Python package:
  - `knapsack.py`: 9-qubit QUBO builder with 4-qubit binary slack encoding ($P=5$).
  - `hardware.py`: Coupling map parser, circulant $C_9(1,2)$ generator, routing analysis.
  - `qaoa.py`: Depth $p=1$ and $p=2$ circuit builders with custom mixer support.
  - `bell.py`: Bell state calibration and tomography across processors.
  - `warm_start.py`: Continuous LP relaxation warm-started state initialization.
  - `zne.py`: Richardson extrapolation zero-noise error mitigation.
  - `noise_model.py`: Realistic IBM calibration noise generator.
  - `qasm_export.py`: OpenQASM 3.0 exporter with duration and pulse timing metadata.
- `processors/` — Hardware JSON topology specifications:
  - `processor_A.json`: 5-qubit linear chain (infeasible / capacity-limited).
  - `processor_B.json`: 9-qubit reference heavy-hex architecture (12 edges).
  - `processor_D.json`: Custom 9-qubit 4-regular chordal ring architecture (18 edges).
- `results/` — Scientific artifacts:
  - `tables/results.csv`: Benchmark results across Processors A, B, and D.
  - `tables/bell.csv`: Bell state state-fidelity measurements.
  - `figures/`: High-resolution PNGs illustrating connectivity, Pareto trade-offs, and energy landscapes.
- `frontend/` — Standalone evaluation hub with zero external network dependencies.
- `report.pdf` & `report.md` — Formal 14-section technical research report.
- `PITCH_SCRIPT.md` — Synchronized 3-minute video presentation script.
