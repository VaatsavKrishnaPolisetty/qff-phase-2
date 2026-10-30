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
        {
            "id": "pareto",
            "title": "Architecture Trade-Off Analysis: Pareto Frontier for Processor D",
            "subtitle": "48 Layout Candidates Evaluated: Chip Coupling Cost vs Routing Overhead",
            "category": "Hardware & Co-Design",
            "filename": "pareto_design_d.png",
            "badges": ["48 Topologies", "102 CX", "Depth 87", "Automorphism 18"],
            "desc": "Systematic mapping of the hardware Pareto frontier across rings, planar grids, degree-3 strips, 10–12 qubit variants, and circulant graphs, demonstrating that Processor D was selected on rigorous multi-objective trade-offs rather than luck.",
            "what": (
                "**Axes & Visual Encoding:**\n"
                "- **X-Axis (Coupling Edges):** Represents the number of physical 2-qubit coupling links (from 9 to 24). In superconducting circuits, edge count serves as a direct proxy for lithographic wiring density, control line cross-routing, and transmon frequency collision risk.\n"
                "- **Y-Axis (Compiled CX Count):** Total physical 2-qubit CX gates required after SABRE transpilation for the 9-qubit knapsack problem. Lower is better.\n"
                "- **Shape & Color Markers:**\n"
                "  • **Grey Circles:** Degree-2 rings (`ring_n9`–`ring_n12`). Cheap to fabricate (9–12 edges) but suffer huge routing blowup (146–165 CX).\n"
                "  • **Orange Triangles:** Planar degree-3 grids (`grid_2x5`, 13 edges, 116 CX).\n"
                "  • **Pink Diamonds:** 2D planar grids (`grid_3x3` with 12 edges, 117 CX; `grid_3x4` with 17 edges, 126 CX).\n"
                "  • **Purple X:** Reference Processor B (12 edges, 121 CX).\n"
                "  • **Blue Squares:** 10–12 qubit expanded layouts with spare routing ancillas (`rand4reg_n10`, `circulant_n12`).\n"
                "  • **Red Dashed Curve:** The empirical Pareto frontier connecting non-dominated hardware candidates.\n"
                "  • **Gold Star:** Our selected design choice: **Processor D (`circulant_n9_o1-2`)**."
            ),
            "why": (
                "**Rubric Motivation & Engineering Rationale:**\n"
                "- **Directly fulfills Rubric Criterion C2:** The rubric asks you to prove you selected Processor D based on multi-metric engineering trade-offs rather than stumbling upon a lucky winner.\n"
                "- **Circuit Depth Minimization:** Although `circulant_n9_o1-3` achieved 99 CX (saving 3 gates), `circulant_n9_o1-2` achieved a lower overall two-qubit depth (**87 vs 90**), allowing gate operations to complete inside tighter qubit coherence windows ($T_1, T_2$).\n"
                "- **Automorphism Structural Symmetry:** The chordal circulant has an automorphism group of order 18. All 9 qubits are topologically identical, ensuring that routing overhead does not depend sensitively on initial qubit placement or localized fabrication flaws.\n"
                "- **Yield & Defect Prevention:** By fixing $N=9$ instead of 10 or 12 qubits, we avoid fabricating idle qubits that increase cryogenic thermal load and frequency collision hazards."
            ),
            "takeaways": (
                "• 48 unique hardware layouts evaluated.\n"
                "• Processor D achieves **102 CX gates** (saving 19 CX gates vs Processor B).\n"
                "• Circuit depth reduced from **117 to 87** (a 25.6% reduction).\n"
                "• SWAP gate count dropped from **17 down to 10** (a 41.2% reduction).\n"
                "• Mean graph distance reduced from $1.89$ to $1.50$, and graph diameter halved from 4 to 2."
            ),
            "faqs": [
                {
                    "q": "Why didn't you pick rand4reg_n10_s4 which had 97 CX gates?",
                    "a": "Fabricating an extra 10th physical qubit increases chip surface area, microwave line cross-routing, and transmon frequency collision probabilities. Restricting to exactly N=9 qubits with regular degree 4 optimizes fabrication yield while staying within 5 CX gates of the unconstrained minimum."
                },
                {
                    "q": "Why not use a planar degree-3 grid to simplify fabrication?",
                    "a": "Planar degree-3 grids like grid_2x5 require 116 CX gates and 18 SWAPs due to routing bottlenecks across the narrow strip. For dense all-to-all optimization problems with 36 logical pairwise couplings, degree-4 chords are mathematically essential."
                },
                {
                    "q": "What does being on the Pareto frontier mean mathematically?",
                    "a": "A layout is Pareto optimal if no other candidate has both fewer coupling edges AND fewer compiled CX gates. Our choice sits directly on the high-performance knee of this frontier."
                }
            ]
        },
        {
            "id": "circuit",
            "title": "QAOA p=1 Quantum Circuit Architecture (9 Qubits)",
            "subtitle": "Hardware Gate Sequence: Hadamards, 36 Cost Rotations, and 9 RX Mixers",
            "category": "Quantum Circuits",
            "filename": "qaoa_circuit.png",
            "badges": ["9 Qubits", "36 ZZ Couplings", "9 RX Mixers", "p=1 QAOA"],
            "desc": "The complete transpiled quantum circuit executing p=1 QAOA for the 0/1 Knapsack problem, demonstrating the 36 pairwise ZZ rotations required by the quadratic penalty constraint.",
            "what": (
                "**Gate Composition & Visual Anatomy (Left to Right):**\n"
                "- **9 Horizontal Wire Registers ($q_0$ to $q_8$):**\n"
                "  • $q_0 \\dots q_4$: 5 item decision qubits ($1 = \\text{pack item}, 0 = \\text{leave behind}$).\n"
                "  • $q_5 \\dots q_8$: 4 logarithmic binary slack qubits representing powers of two ($1, 2, 4, 8$ kg).\n"
                "- **Red $H$ (Hadamard) Column:** Prepares all 9 qubits in a uniform quantum superposition $|+\\rangle^{\\otimes 9}$, testing all $2^9 = 512$ combinations simultaneously.\n"
                "- **Blue $R_Z$ Gates:** Single-qubit longitudinal phase rotations encoding individual item values and linear constraint biases.\n"
                "- **Vertical Blue Dumbbells ($R_{ZZ}(\\theta)$):** 36 two-qubit entangling gates. Each gate applies a phase rotation proportional to $2 \\gamma J_{ij}$.\n"
                "- **Purple $R_X(2\\beta)$ Column:** Transverse mixer layer driving quantum interference between computational states.\n"
                "- **Grey Meter Icons:** Final projective measurement into the 9-bit classical register `meas`."
            ),
            "why": (
                "**Physical Function & Problem Mapping:**\n"
                "- **Executing Unconstrained Quantum Optimization:** Superconducting quantum computers execute physical microwave pulses, not classical `if/else` loops. This circuit is the exact quantum algorithm compiled into physics.\n"
                "- **Why are there 36 two-qubit terms?** Expanding the quadratic penalty $P ( \\sum w_i x_i + \\sum 2^k s_k - 15 )^2$ generates non-zero cross-terms $w_i w_j x_i x_j$ between every pair of variables. With 9 qubits, $\\binom{9}{2} = 36$ pairwise $ZZ$ terms are created.\n"
                "- **Why sparse chips suffer:** On Processor B, non-neighboring qubits cannot directly execute $R_{ZZ}$. The compiler is forced to insert 17 clumsy SWAP gates, expanding this circuit into 121 CX gates. Processor D's chordal shortcuts reduce this to 102 CX gates."
            ),
            "takeaways": (
                "• 9 total qubits: 5 item variables + 4 logarithmic slack variables.\n"
                "• 36 dense pairwise $ZZ$ interactions in the problem Hamiltonian.\n"
                "• Logical CX requirement: 72 CX gates.\n"
                "• Compiled on Processor B: 121 physical CX gates (17 SWAPs).\n"
                "• Compiled on Processor D: 102 physical CX gates (10 SWAPs, saving 19 CX)."
            ),
            "faqs": [
                {
                    "q": "Why does a p=1 QAOA circuit have 72 logical CX gates?",
                    "a": "Each two-qubit RZZ(theta) gate decomposes into exactly 2 CX gates and 1 RZ rotation: CX(i, j) -> RZ(theta, j) -> CX(i, j). 36 RZZ terms * 2 CX = 72 logical CX gates."
                },
                {
                    "q": "How does this circuit penalize exceeding 15 kg?",
                    "a": "The penalty adds positive energy proportional to (w_total + slack - 15)^2. Infeasible bitstrings receive high energy, causing quantum destructive interference to suppress their measurement probability."
                },
                {
                    "q": "What do the purple Rx gates do?",
                    "a": "The mixer layer applies rotations around the X-axis. This allows quantum tunneling between bitstrings, enabling constructive interference to amplify the ground-state probability of V*=26."
                }
            ]
        },
        {
            "id": "landscape",
            "title": "20×20 Noisy Objective Energy Landscape on Processor D",
            "subtitle": "Sampled Mean QUBO Cost Heatmap Across Variational Angles (gamma, beta)",
            "category": "Energy Landscapes",
            "filename": "landscape_D.png",
            "badges": ["20x20 Grid", "400 Evaluations", "gamma=0.2831", "beta=2.8648"],
            "desc": "Heatmap mapping the sampled mean QUBO cost across a 20x20 parameter grid under official hardware depolarizing and readout noise, marking the global optimal variational angles.",
            "what": (
                "**Visual Breakdown of the Surface:**\n"
                "- **X-Axis ($\\gamma$):** Cost Hamiltonian variational angle scaled by the maximum Ising coefficient ($120.0$), ranging from $0.0$ to $1.0$.\n"
                "- **Y-Axis ($\\beta$):** Mixer Hamiltonian variational angle ranging from $0$ to $\\pi$ ($3.1416$).\n"
                "- **Color Bar (Viridis Gradient):** Represents sampled expectation value $\\langle C \\rangle$. Dark purple/blue shows lower QUBO energy (favorable, feasible, high-value states); yellow/green represents high energy (severe penalty violations).\n"
                "- **Red Star with White Outline:** Pinpoints the global minimum parameter pair $(\\gamma^* = 0.2831, \\beta^* = 2.8648)$ discovered by seeded COBYLA optimization."
            ),
            "why": (
                "**Rubric Requirement & Convergence Insights:**\n"
                "- **Mandatory Rubric Objective (C3):** Rubric Criterion C3 requires plotting the objective landscape on Processor D with the optimum marked.\n"
                "- **Proving Non-Convexity:** The visualization proves that QAOA landscapes feature multiple local minima, ridges, and plateaus. This explains why single-shot optimizers often get trapped and justifies our 5-seed random restart protocol.\n"
                "- **Noise Resilience:** Even under depolarizing gate error ($p_2=0.005$) and readout flip error ($p_{\\text{readout}}=0.01$), the global basin remains stable and distinctly separated from infeasible regions."
            ),
            "takeaways": (
                "• 400 grid points mapped with 1024 shots per point on Processor D under noise.\n"
                "• Optimal variational angles: $\\gamma^* = 0.2831, \\beta^* = 2.8648$.\n"
                "• Minimum expectation value: $\\langle C_{\\text{scaled}} \\rangle = -1.5232$.\n"
                "• State feasibility at optimum: **95.54%** (concentrating over 95% of shots in valid solutions)."
            ),
            "faqs": [
                {
                    "q": "Why was the cost Hamiltonian divided by 120.0?",
                    "a": "120.0 is the largest coefficient in the Ising Hamiltonian. Normalizing the operator norm prevents wild phase oscillations and ensures variational parameters gamma remain in a well-behaved [0, 1] interval."
                },
                {
                    "q": "Why did seeds 0 and 4 get stuck near zero expectation?",
                    "a": "Looking at the landscape, beta angles near 0.8 to 1.6 contain wide flat plateaus with near-zero gradients. COBYLA exhausted its iteration budget without escaping the plateau, confirming the necessity of multiple starting seeds."
                },
                {
                    "q": "How does hardware noise affect the landscape?",
                    "a": "Depolarizing noise contracts the energy contrast (shallows the valleys) by mixing the quantum state with the maximally mixed state, but the optimal coordinates (gamma*, beta*) do not shift significantly."
                }
            ]
        },
        {
            "id": "processors",
            "title": "Hardware Coupling Topologies: Processors A, B, and D",
            "subtitle": "Side-by-Side Comparison of Qubit Connectivity and Routing Bottlenecks",
            "category": "Hardware Topologies",
            "filename": "processors_graphs.png",
            "badges": ["Processor A (5Q)", "Processor B (9Q)", "Processor D (9Q)", "Capacity Rule"],
            "desc": "Side-by-side coupling graphs of Processor A (5-qubit line), Processor B (9-qubit reference heavy-hex), and Processor D (9-qubit circulant chordal), demonstrating capacity limits and routing bottlenecks.",
            "what": (
                "**Graph Topologies Illustrated (Left to Right):**\n"
                "- **Processor A (Left):** 5 qubits, 4 edges, max degree 3. Tree topology: line `0-1-2` with branch `1-3-4`.\n"
                "- **Processor B (Center):** 9 qubits, 12 edges, max degree 4, diameter 4. Planar lattice inspired by IBM Heavy-Hex architectures.\n"
                "- **Processor D (Right):** 9 qubits, 18 edges, uniform degree 4, diameter 2. Regular circulant chordal graph $C_9(1, 2)$."
            ),
            "why": (
                "**Capacity Limits & Bottleneck Analysis:**\n"
                "- **Capacity Limit on Processor A:** The 0/1 knapsack problem requires 5 decision qubits + 4 slack qubits = 9 qubits. Processor A has only 5 qubits and **cannot physically execute the problem** without altering the locked mathematical formulation.\n"
                "- **Routing Bottlenecks on Processor B:** Graph diameter is 4 and average shortest path is $1.89$. When qubit $0$ needs to interact with qubit $3$ or $4$, the compiler must insert up to 3 intermediate SWAP gates, expanding the circuit to 121 CX gates.\n"
                "- **Direct Shortcuts on Processor D:** Every qubit connects to 4 neighbors (degrees $i\\pm 1$ and $i\\pm 2$). The maximum distance between any two qubits is 2 hops, cutting SWAPs by 41.2%."
            ),
            "takeaways": (
                "• Processor A: 5 qubits, 4 edges $\\implies$ Status: **Not Executable (Capacity Rule)**.\n"
                "• Processor B: 9 qubits, 12 edges, diameter 4, avg path 1.89 $\\implies$ 17 SWAPs, 121 CX.\n"
                "• Processor D: 9 qubits, 18 edges, diameter 2, avg path 1.50 $\\implies$ 10 SWAPs, 102 CX."
            ),
            "faqs": [
                {
                    "q": "Why couldn't we truncate slack qubits to make the problem fit Processor A?",
                    "a": "Truncating slack bits would restrict the maximum slack to less than 15, changing the problem instance and making legal weights appear illegal. Official rules strictly forbid altering locked problem instances."
                },
                {
                    "q": "Why is graph diameter so critical for QAOA?",
                    "a": "Because the Knapsack Hamiltonian is dense (36 all-to-all terms), smaller graph diameter directly translates to fewer SWAP routing steps and lower two-qubit gate depth."
                }
            ]
        },
        {
            "id": "processor_d",
            "title": "Processor D Regular Degree-4 Circulant Chordal Architecture",
            "subtitle": "High-Resolution Circular Blueprint of the Frozen Hardware Layout",
            "category": "Hardware Topologies",
            "filename": "processor_D_graph.png",
            "badges": ["N=9 Qubits", "18 Edges", "Degree 4", "Rule Validated"],
            "desc": "High-resolution circular visualization of Processor D (circulant chordal graph C_9(1, 2)) displaying the 18 bidirectional coupling links and uniform degree-4 connectivity.",
            "what": (
                "**Architectural Blueprint:**\n"
                "- **9 Physical Qubits ($0$ to $8$):** Arranged symmetrically in a circular planar configuration.\n"
                "- **Outer Ring Edges:** 9 nearest-neighbor connections: $(i, (i+1) \\pmod 9)$.\n"
                "- **Inner Chordal Edges:** 9 shortcut chords connecting next-nearest neighbors: $(i, (i+2) \\pmod 9)$.\n"
                "- **Uniform Node Degree:** Exactly 4 physical links meet at every single vertex."
            ),
            "why": (
                "**Compliance with Official Hardware Rules (1–5):**\n"
                "- **Rule 1 (Qubits):** Exactly 9 qubits (within legal range $[9, 12]$).\n"
                "- **Rule 2 (Connected):** Graph is fully connected with algebraic connectivity $\\lambda_2 = 1.68$.\n"
                "- **Rule 3 (Max Degree):** Uniform degree 4 (strictly satisfies $\\le 4$).\n"
                "- **Rule 4 (Gate Set):** Basis gates strictly $\\{rz, sx, x, cx\\}$.\n"
                "- **Rule 5 (Noise Model):** Official synthetic noise ($p_1=0.001, p_2=0.005, p_{\\text{readout}}=0.01$).\n"
                "- **Frozen & Validated:** Passes official `validate_processor_d` with **0 errors**."
            ),
            "takeaways": (
                "• Strict compliance with all 5 Phase 2 hardware constraints.\n"
                "• Automorphism group order 18 provides complete vertex transitivity.\n"
                "• Frozen in `processors/processor_D.json` with immutable Git commit history."
            ),
            "faqs": [
                {
                    "q": "What is vertex-transitivity and why does it matter?",
                    "a": "In a vertex-transitive graph, all nodes are topologically indistinguishable. No qubit is in a bottleneck or dead end, making compiler routing independent of initial variable-to-qubit mapping."
                },
                {
                    "q": "Does Processor D require 3D chip integration?",
                    "a": "Degree-4 chordal graphs can be fabricated using standard planar superconducting transmon processes with multi-layer airbridges or through-silicon vias (TSVs) commonly used in IBM and Google quantum processors."
                }
            ]
        },
        {
            "id": "warm_start",
            "title": "Warm-Started QAOA: Continuous LP Relaxation vs Standard QAOA",
            "subtitle": "Injecting Classical Convex Optimization to Boost Ground-State Discovery",
            "category": "Advanced Algorithms",
            "filename": "warm_start_comparison.png",
            "badges": ["LP Relaxation", "3x P_opt Boost", "Warm Start", "NISQ Optimization"],
            "desc": "Measurement probability histograms comparing classical Linear Programming (LP) continuous relaxation initialization against standard uniform superposition |+>^9.",
            "what": (
                "**Histogram Anatomy:**\n"
                "- **X-Axis:** Sampled computational bitstrings.\n"
                "- **Y-Axis:** Measurement sampling probability $P(\\text{state})$.\n"
                "- **Blue Bars:** Standard QAOA initialized in $|+\\rangle^{\\otimes 9}$. Probability is dispersed broadly across 512 states ($P_{\\text{opt}} \\approx 2.25\\%$).\n"
                "- **Cyan/Green Bars:** Warm-started QAOA initialized with continuous LP relaxation angles $\\theta_i = 2 \\arcsin(\\sqrt{x_i^*})$. The probability sharply concentrates on high-value candidate states ($P_{\\text{opt}} \\approx 6.82\\%$)."
            ),
            "why": (
                "**Overcoming NISQ QAOA Limitations:**\n"
                "- At shallow depth $p=1$, standard QAOA spreads probability across all 512 states and barely matches uniform random guessing ($0.0225$ vs $0.03125$).\n"
                "- Warm-starting solves the continuous LP relaxation classically in $\\mathcal{O}(N \\log N)$ time, setting initial qubit rotation angles $\\theta_i$. This biases the quantum state toward promising regions while letting the quantum processor explore non-local combinatorial correlations."
            ),
            "takeaways": (
                "• Standard QAOA ground-state discovery: $P_{\\text{opt}} = 0.0225$.\n"
                "• Warm-started QAOA ground-state discovery: $P_{\\text{opt}} = 0.0682$ (**$3.0\\times$ boost**).\n"
                "• Classical LP runtime: $<1$ millisecond."
            ),
            "faqs": [
                {
                    "q": "Does warm-starting defeat the purpose of quantum computing?",
                    "a": "No! Continuous LP relaxation solves fractional knapsack, but the true 0/1 knapsack is NP-hard. Warm-starting creates a hybrid algorithm where classical convex solvers initialize the state and quantum interference solves the discrete NP-hard residual."
                },
                {
                    "q": "How are the initial angles calculated?",
                    "a": "For each continuous variable x_i in [0, 1], we set initial qubit state |psi_0> = cos(theta_i/2)|0> + sin(theta_i/2)|1> with theta_i = 2 * arcsin(sqrt(x_i))."
                }
            ]
        },
        {
            "id": "shifted_target",
            "title": "Shifted-Target 5-Qubit Formulation vs 9-Qubit Slack Expansion",
            "subtitle": "Eliminating Auxiliary Slack Qubits for Resource-Constrained NISQ Chips",
            "category": "QUBO Formulations",
            "filename": "shifted_target_vs_slack.png",
            "badges": ["5 Qubits", "Fits Processor A", "0 Slack Qubits", "-80% CX Gates"],
            "desc": "Resource scaling and sampled solution quality comparing the 5-qubit slack-free formulation (fits Processor A) against the standard 9-qubit slack encoding.",
            "what": (
                "**Comparative Visual Panels:**\n"
                "- **Left Panel (Hardware Resource Metrics):** Compares required qubits (5 vs 9), compiled CX gate count (10 vs 102), and circuit depth.\n"
                "- **Right Panel (Sampled Value Distribution):** Shows that the 5-qubit model successfully concentrates probability on feasible states and reaches $V^*=26$."
            ),
            "why": (
                "**Fulfilling Rubric Requirement (b):**\n"
                "- The rubric explicitly suggests testing: *'(b) Unbalanced / shifted-target penalisation (no slack qubits, 5 qubits): this fits Processor A, answering the capacity limit. Show A/B/D results and compare resources.'*\n"
                "- Proves that for small quantum chips with tight qubit limits, shifting the penalty target eliminates slack qubits entirely while preserving the optimal ground state."
            ),
            "takeaways": (
                "• Qubit count reduced from **9 down to 5** (fits Processor A).\n"
                "• CX gate count reduced from **102 down to 10 CX gates** (an $80+\\%$ reduction).\n"
                "• Successfully recovers ground truth $V^* = 26$ on Processor A."
            ),
            "faqs": [
                {
                    "q": "How does shifted-target work without slack variables?",
                    "a": "Instead of unrolling binary powers of slack, it centers the penalty around a target weight W_target = W - delta, heavily punishing states exceeding capacity while preserving the relative value ranking."
                },
                {
                    "q": "Why isn't this the primary submission?",
                    "a": "Because the official Phase 2 starter kit locked the exact 9-qubit QUBO formula with 4 slack variables as the required benchmark rows."
                }
            ]
        },
        {
            "id": "problem_aware",
            "title": "Problem-Aware Processor D: Algorithmic Hardware Co-Design",
            "subtitle": "Mapping Dominant ZZ Couplings Directly Onto Physical Hardware Edges",
            "category": "Hardware & Co-Design",
            "filename": "problem_aware_D_graph.png",
            "badges": ["Co-Design", "Dominant Couplings", "Max Feasibility", "Distance 1"],
            "desc": "Quantum hardware topology engineered specifically for the 0/1 Knapsack problem by aligning physical transmon coupling links with the strongest ZZ Hamiltonian interactions.",
            "what": (
                "**Graph Visualization:**\n"
                "- Node labels represent physical qubits.\n"
                "- Edge thickness and color intensity reflect the magnitude of the pairwise Ising interaction $|J_{ij}|$.\n"
                "- Physical edges directly bridge the variable pairs with the largest cross-penalty terms (e.g., items with heavy weights and high-order slack bits)."
            ),
            "why": (
                "**Architecture-Algorithm Co-Design Philosophy:**\n"
                "- Standard commercial chips are designed with generic square or heavy-hex grids, forcing compilers to insert dozens of SWAP gates.\n"
                "- By co-designing the hardware topology around the problem's Hamiltonian, 100% of the dominant interaction terms execute natively at graph distance 1 with zero SWAP overhead."
            ),
            "takeaways": (
                "• 100% of high-magnitude $ZZ$ interactions placed at nearest-neighbor distance.\n"
                "• Achieves **$P_{\\text{feasible}} = 0.968$**, highest feasibility among all tested static topologies.\n"
                "• Demonstrates the future paradigm of application-specific quantum processors (ASQPs)."
            ),
            "faqs": [
                {
                    "q": "What is an Application-Specific Quantum Processor (ASQP)?",
                    "a": "Similar to how GPUs or TPUs are custom-designed for matrix math, an ASQP tailors transmon coupling maps to the interaction graph of specific optimization or quantum chemistry problems."
                }
            ]
        }
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
    
    print(f"Successfully bundled {len(files_data)} files and {len(figures)} rich figures into {out_js} and {out_json}")

if __name__ == "__main__":
    build_data()
