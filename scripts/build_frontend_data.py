"""Packs all repository files, metrics, and figures metadata into a unified JSON bundle for the frontend."""

import json
from pathlib import Path

def build_data():
    root = Path(__file__).resolve().parent.parent
    
    file_manifest = [
        {"path": "report.md", "category": "Documentation", "title": "Comprehensive Research Report (8 Sections)"},
        {"path": "README.md", "category": "Documentation", "title": "Judges Instructions & Key Results"},
        {"path": "PITCH_SCRIPT.md", "category": "Documentation", "title": "3-Minute Video Pitch Script"},
        {"path": "requirements.txt", "category": "Engineering", "title": "Pinned Dependency Manifest"},
        {".github/workflows/ci.yml": "ci.yml"},
        {"path": ".github/workflows/ci.yml", "category": "Engineering", "title": "GitHub Actions CI Workflow"},
        
        {"path": "processors/processor_A.json", "category": "Processors", "title": "Processor A (5Q Line Topology)"},
        {"path": "processors/processor_B.json", "category": "Processors", "title": "Processor B (9Q Reference)"},
        {"path": "processors/processor_D.json", "category": "Processors", "title": "Processor D (9Q Circulant Chordal - Frozen)"},
        
        {"path": "results/tables/results.csv", "category": "Required Benchmarks", "title": "Official Benchmark Results (A, B, D)"},
        {"path": "results/tables/results_detail.csv", "category": "Required Benchmarks", "title": "Detailed Probabilities & Ground State Discovery"},
        {"path": "results/tables/bell.csv", "category": "Required Benchmarks", "title": "Bell State Preparation & Fidelity Verification"},
        {"path": "results/tables/resources.csv", "category": "Required Benchmarks", "title": "Transpiled Hardware Resource Overhead Metrics"},
        {"path": "results/tables/summary_for_readme.csv", "category": "Required Benchmarks", "title": "Executive Summary Table"},
        {"path": "results/tables/d_search.csv", "category": "Required Benchmarks", "title": "Topology Exploration (48 Graph Architectures)"},
        {"path": "results/tables/qaoa_seeds.csv", "category": "Required Benchmarks", "title": "QAOA Seeds 0-4 Parameter Optimization"},
        
        {"path": "results/extra/pareto_candidates.csv", "category": "Extra Experiments", "title": "Pareto Frontier Architectural Candidates"},
        {"path": "results/extra/case_study_scaling.csv", "category": "Extra Experiments", "title": "Disaster Relief Multi-Constraint Qubit Scaling"},
        {"path": "results/extra/ibm_calibration_table.csv", "category": "Extra Experiments", "title": "IBM Quantum Hardware Backend Calibration"},
        {"path": "results/extra/ibm_noise_results.csv", "category": "Extra Experiments", "title": "IBM Calibration Noise vs Synthetic Depolarizing"},
        {"path": "results/extra/hardware_timing_analysis.csv", "category": "Extra Experiments", "title": "Hardware Pulse Schedule Timing & Latency Budget"},
        {"path": "results/extra/processor_D_circuit.qasm", "category": "Extra Experiments", "title": "OpenQASM 3.0 Hardware Circuit Export"},
        {"path": "results/extra/penalty_sweep.csv", "category": "Extra Experiments", "title": "Penalty Sweep P in {2, 5, 10, 20} Analysis"},
        {"path": "results/extra/shifted_target_results.csv", "category": "Extra Experiments", "title": "Shifted Target 5-Qubit Formulation on Processor A"},
        {"path": "results/extra/shifted_target_resources.csv", "category": "Extra Experiments", "title": "Shifted Target Gate Resources"},
        {"path": "results/extra/p2_results.csv", "category": "Extra Experiments", "title": "Depth p=2 QAOA Evaluation"},
        {"path": "results/extra/zne_results.csv", "category": "Extra Experiments", "title": "Zero-Noise Extrapolation (Unitary Folding)"},
        {"path": "results/extra/warm_start_results.csv", "category": "Extra Experiments", "title": "Warm-Started Continuous LP Relaxation"},
        {"path": "results/extra/cvar_results.csv", "category": "Extra Experiments", "title": "Conditional Value-at-Risk (CVaR) Optimization"},
        {"path": "results/extra/cp_mixer_results.csv", "category": "Extra Experiments", "title": "Constraint-Preserving Mixer QAOA"},
        {"path": "results/extra/cvar_cp_results.csv", "category": "Extra Experiments", "title": "Combined CVaR + Constraint-Preserving Mixer"},
        {"path": "results/extra/rqaoa_results.csv", "category": "Extra Experiments", "title": "Recursive QAOA (RQAOA) Correlation Reduction"},
        {"path": "results/extra/adaptive_penalty_results.csv", "category": "Extra Experiments", "title": "Adaptive Penalty Homotopy Continuation"},
        {"path": "results/extra/gas_results.csv", "category": "Extra Experiments", "title": "Grover Adaptive Search (GAS)"},
        {"path": "results/extra/mem_results.csv", "category": "Extra Experiments", "title": "Measurement Error Mitigation (MEM)"},
        
        {"path": "src/knapsack.py", "category": "Source Code", "title": "0/1 Knapsack QUBO & Ising Hamiltonian"},
        {"path": "src/qaoa_numpy.py", "category": "Source Code", "title": "Classical QAOA Simulator & Statevector Engine"},
        {"path": "src/processors.py", "category": "Source Code", "title": "Hardware Processors & Rule Validator"},
        {"path": "src/circuits.py", "category": "Source Code", "title": "Qiskit Quantum Circuit Builder & Transpiler"},
        {"path": "src/bell.py", "category": "Source Code", "title": "Bell State Preparation & Pauli Correlation"},
        {"path": "src/landscape.py", "category": "Source Code", "title": "2D Energy Landscape Mapping Engine"},
        {"path": "src/case_study.py", "category": "Source Code", "title": "Disaster Relief Multi-Constraint QUBO Generator"},
        {"path": "src/pareto_plot.py", "category": "Source Code", "title": "Hardware Pareto Frontier Plot Generator"},
        {"path": "src/adaptive_penalty.py", "category": "Source Code", "title": "Homotopy Penalty Continuation Algorithm"},
        {"path": "src/gas.py", "category": "Source Code", "title": "Grover Adaptive Search Implementation"},
        {"path": "src/rqaoa.py", "category": "Source Code", "title": "Recursive QAOA Qubit Elimination"},
        {"path": "src/mitigation.py", "category": "Source Code", "title": "Readout Error Mitigation & ZNE"},
        
        {"path": "tests/check_formulation.py", "category": "Test Suite", "title": "Fast Zero-Dependency Formulation Checker"},
        {"path": "tests/test_knapsack.py", "category": "Test Suite", "title": "Pytest: Knapsack QUBO & Ground Truth"},
        {"path": "tests/test_circuits.py", "category": "Test Suite", "title": "Pytest: Quantum Circuits & Bell Formulas"},
        {"path": "tests/test_processors.py", "category": "Test Suite", "title": "Pytest: Hardware Rules & Dual Validation"},
        {"path": "tests/test_case_study.py", "category": "Test Suite", "title": "Pytest: Multi-Constraint Scaling & Disaster Relief"},
    ]
    
    files_data = []
    for item in file_manifest:
        if "path" not in item:
            continue
        p = root / item["path"]
        if p.exists():
            try:
                content = p.read_text(encoding="utf-8")
                files_data.append({
                    "path": item["path"],
                    "filename": p.name,
                    "category": item["category"],
                    "title": item["title"],
                    "extension": p.suffix.lstrip("."),
                    "size": p.stat().st_size,
                    "content": content
                })
            except Exception as e:
                print(f"Error reading {p}: {e}")
        else:
            print(f"File not found: {p}")
            
    figures = [
        {"id": "pareto", "title": "Architecture Pareto Frontier (CX vs Edges)", "filename": "pareto_design_d.png", "desc": "Pareto trade-off curve across 48 layouts showing Processor D choice minimizing depth (87) with 18 edges."},
        {"id": "circuit", "title": "QAOA p=1 Quantum Circuit (9 Qubits)", "filename": "qaoa_circuit.png", "desc": "Hardware circuit showing 9 Hadamards, 36 pairwise ZZ rotations, and 9 RX mixers."},
        {"id": "landscape", "title": "Noisy Objective Landscape on Processor D", "filename": "landscape_D.png", "desc": "20x20 grid mapping mean QUBO cost with global optimum marked at gamma=0.2831, beta=2.8648."},
        {"id": "processors", "title": "Coupling Graphs: Processor A, B, and D", "filename": "processors_graphs.png", "desc": "Comparison of A (5Q line), B (9Q heavy-hex), and D (9Q circulant chordal)."},
        {"id": "processor_d", "title": "Processor D Chordal Architecture", "filename": "processor_D_graph.png", "desc": "High-resolution circular visualization of the regular degree-4 circulant layout."},
        {"id": "warm_start", "title": "Warm-Started QAOA (Continuous LP Relaxation)", "filename": "warm_start_comparison.png", "desc": "Measurement distribution comparing LP continuous relaxation initialization vs standard QAOA."},
        {"id": "unbalanced", "title": "Shifted Target vs Slack Binary Expansion", "filename": "shifted_target_vs_slack.png", "desc": "Comparison of 5-qubit slack-free formulation (fits Processor A) vs standard 9-qubit slack encoding."},
        {"id": "problem_aware", "title": "Problem-Aware Processor D Co-Design", "filename": "problem_aware_D_graph.png", "desc": "Algorithmic hardware co-design placing dominant ZZ Hamiltonian interactions directly on physical edges."}
    ]
    
    bundle = {
        "team": "Emerging Genius",
        "problem": "PS-O3: Resource-Constrained Item Selection (0/1 Knapsack)",
        "ground_truth": {
            "v_star": 26,
            "optimal_items": [1, 2, 3, 4],
            "optimal_weight": 14,
            "max_weight": 15,
            "slack_qubits": 4,
            "total_qubits": 9,
            "feasible_subsets": 28,
            "random_baseline_feasible": 0.8750,
            "random_baseline_optimal": 0.03125
        },
        "rubric_summary": {
            "processor_a": "Not executable: needs 9 qubits, has 5",
            "processor_b": {"cx": 121, "depth": 117, "swaps": 17, "p_feasible_noisy": 0.9434, "p_opt_noisy": 0.0249, "noisy_cost": 82.85},
            "processor_d": {"cx": 102, "depth": 87, "swaps": 10, "p_feasible_noisy": 0.9421, "p_opt_noisy": 0.0225, "noisy_cost": 74.96},
            "swap_reduction_pct": 41.18,
            "cx_reduction_pct": 15.70,
            "depth_reduction_pct": 25.64,
            "bell_adjacent_fidelity": "0.9633 ± 0.0021",
            "bell_farthest_fidelity": "0.9548 ± 0.0023",
            "processor_d_validation": "0 errors (Strict pass on Rules 1-5)"
        },
        "figures": figures,
        "files": files_data
    }
    
    out_js = root / "frontend" / "projectData.js"
    out_json = root / "frontend" / "src" / "data" / "projectData.json"
    
    out_js.parent.mkdir(parents=True, exist_ok=True)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    
    # Write as JS window/global variable export
    js_content = f"window.PROJECT_DATA = {json.dumps(bundle, indent=2)};"
    out_js.write_text(js_content, encoding="utf-8")
    
    # Write as pure JSON
    out_json.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    
    print(f"Successfully bundled {len(files_data)} files into {out_js} and {out_json}")

if __name__ == "__main__":
    build_data()

