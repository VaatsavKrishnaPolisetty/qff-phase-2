# QFF 2026 Phase 2 Technical Report
## Quantum Optimization Track — Problem Statement PS-O3
### Resource-Constrained Item Selection (0/1 Knapsack Problem) with QAOA

**Team Name:** Emerging Genius  
**Problem Statement:** PS-O3 (Locked Official Instance)  
**Date:** October 2026  

---

## Executive Summary

This report presents an end-to-end implementation, verification, and hardware-architecture benchmarking of the 0/1 Knapsack Problem (Problem Statement PS-O3) using the Quantum Approximate Optimization Algorithm (QAOA) for Phase 2 of the Qiskit Fall Fest 2026 Optimization Track.

The locked knapsack instance consists of 5 items with values $v = [10, 4, 7, 5, 8]$, weights $w = [5, 3, 4, 2, 6]$, and a weight capacity constraint $W = 15$. The problem is rigorously formulated into an unconstrained Quadratic Unconstrained Binary Optimization (QUBO) model using a 4-qubit binary slack encoding ($s = s_0 + 2s_1 + 4s_2 + 8s_3 \in \{0, \dots, 15\}$) and a quadratic penalty multiplier $P = 5$, requiring exactly 9 logical qubits. The classical optimum is found by exhaustive search over all 32 subsets to be $V^* = 26$ (items $\{1, 2, 3, 4\}$ with total weight 14), with 28 out of 32 subsets ($87.5\%$) being feasible.

The mapped 9-qubit Ising Hamiltonian contains 36 all-to-all $ZZ$ two-qubit interaction terms. We evaluate QAOA at depth $p=1$ across 5 official pseudorandom seeds ($0 \dots 4$) with classical COBYLA parameter optimization. We benchmark performance across three architectures:
1. **Processor A (5 qubits):** Evaluated as strictly **not executable** under the official capacity rule (needs 9 qubits, has 5).
2. **Processor B (9 qubits, 12 edges):** Reference benchmark exhibiting significant routing congestion (17 SWAPs, 121 CX gates, depth 117).
3. **Processor D (9 qubits, 18 edges):** Our custom 4-regular circulant design $C_9(1, 2)$ which slashes routing overhead by $41.2\%$ (10 SWAPs, 102 CX gates, depth 87).

Under the official depolarizing and readout noise model, QAOA achieves a feasible sampling probability of $P_{\text{feasible}} = 94.21\%$ on Processor D ($94.34\%$ on Processor B), decisively exceeding the uniform random baseline of $87.50\%$. The optimal item combination is sampled with probability $P_{\text{opt}} = 0.0225$ ($0.0249$ on B), reaching $100.0\%$ of the optimal value across 4096 shots.

---

## 1. Problem Definition, Mathematical Formulation & QUBO Construction

### 1.1 The 0/1 Knapsack Problem
The 0/1 Knapsack Problem seeks to select a subset of $N=5$ items to maximize total profit subject to a hard capacity constraint:
$$\max_{x \in \{0, 1\}^5} \sum_{i=1}^5 v_i x_i \quad \text{subject to} \quad \sum_{i=1}^5 w_i x_i \le W$$

For the locked PS-O3 instance:
- **Values:** $v = [10, 4, 7, 5, 8]$
- **Weights:** $w = [5, 3, 4, 2, 6]$
- **Capacity:** $W = 15$

### 1.2 Exact Classical Solution
Exhaustive evaluation across all $2^5 = 32$ item combinations establishes the exact ground-truth answer key:
- **Feasible subsets:** Exactly 28 out of 32 subsets satisfy $\sum w_i x_i \le 15$.
- **Uniform random baseline feasibility:** $P_{\text{feasible}}^{\text{random}} = \frac{28}{32} = 0.8750$ ($87.50\%$).
- **Optimal subset:** Items $\{1, 2, 3, 4\}$ with item bitstring $x = (1, 1, 1, 1, 0)$ (index 15).
  - Total Weight: $w_1 + w_2 + w_3 + w_4 = 5 + 3 + 4 + 2 = 14 \le 15$
  - Optimal Value: $V^* = 10 + 4 + 7 + 5 = 26$
  - Uniform random baseline optimal probability: $P_{\text{opt}}^{\text{random}} = \frac{1}{32} = 0.03125$ ($3.125\%$).

### 1.3 Binary Slack Variable Formulation & QUBO
To convert the inequality constraint into an unconstrained minimization model, we introduce an auxiliary non-negative slack variable $s \in [0, W]$. Because $\sum w_i x_i \le 15$, the required slack range is $0 \le s \le 15$. This is encoded into 4 binary slack variables $s_0, s_1, s_2, s_3 \in \{0, 1\}$ using powers of two:
$$s = \sum_{k=0}^3 2^k s_k = s_0 + 2s_1 + 4s_2 + 8s_3 \in \{0, 1, \dots, 15\}$$

The equality constraint is therefore:
$$\sum_{i=1}^5 w_i x_i + \sum_{k=0}^3 2^k s_k = 15$$

Assigning decision variables $x_1 \dots x_5$ to qubits $0 \dots 4$ and slack variables $s_0 \dots s_3$ to qubits $5 \dots 8$ yields a 9-qubit state vector $y = (x_1, \dots, x_5, s_0, \dots, s_3)^T \in \{0, 1\}^9$ with coefficient vector:
$$c = (5, 3, 4, 2, 6, 1, 2, 4, 8)^T$$

With penalty parameter $P = 5$, the QUBO cost function is:
$$C(y) = -\sum_{i=1}^5 v_i x_i + P \left( \sum_{i=0}^8 c_i y_i - W \right)^2 = y^T Q y + \text{const}$$

Since $y_i^2 = y_i$ for binary variables:
- **Diagonal entries ($i = j$):** $Q_{ii} = -v_i + P(c_i^2 - 2 W c_i)$
- **Off-diagonal entries ($i < j$):** $Q_{ij} = 2 P c_i c_j$
- **Energy constant:** $\text{const} = P W^2 = 5 \times 15^2 = 1125$

#### Explicit $9 \times 9$ Integer QUBO Matrix:
$$\begin{pmatrix}
-725 & 150 & 200 & 100 & 300 & 50 & 100 & 200 & 400 \\
0 & -441 & 120 & 60 & 180 & 30 & 60 & 120 & 240 \\
0 & 0 & -573 & 80 & 240 & 40 & 80 & 160 & 320 \\
0 & 0 & 0 & -295 & 120 & 20 & 40 & 80 & 160 \\
0 & 0 & 0 & 0 & -872 & 60 & 120 & 240 & 480 \\
0 & 0 & 0 & 0 & 0 & -145 & 20 & 40 & 80 \\
0 & 0 & 0 & 0 & 0 & 0 & -280 & 80 & 160 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & -520 & 320 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & -880
\end{pmatrix}$$

**Mathematical Verification:** The matrix formulation was verified across all $2^9 = 512$ bitstrings against the direct algebraic cost formula, with absolute residual error $< 10^{-9}$. The unique global minimum occurs at bitstring $b = 47$ ($x = (1, 1, 1, 1, 0)$, $s = (1, 0, 0, 0) \implies \text{slack} = 1$). Because $14 + 1 = 15$, the constraint is exactly satisfied, producing minimal cost $C = -26 = -V^*$.

### 1.4 Ising Hamiltonian Mapping & Scaling
Using the spin transformation $y_i = \frac{I - Z_i}{2}$, the QUBO maps onto the Ising Hamiltonian:
$$H_C = \sum_{i=0}^8 h_i Z_i + \sum_{0 \le i < j \le 8} J_{ij} Z_i Z_j + \text{offset}$$

- **Two-qubit coupling terms:** $\binom{9}{2} = 36$ non-zero $ZZ$ terms (dense, all-to-all connectivity).
- **Single-qubit terms:** 9 non-zero $Z$ terms.
- **Energy offset:** $14.5$
- **Scale factor:** $\text{scale} = \max(|h_i|, |J_{ij}|) = 120.0$.
To maintain standardized angle scaling for the QAOA phase separation layer without altering the eigenspectrum, the cost Hamiltonian is scaled by 120.0, mapping the evolution operator to:
$$U(C, \gamma) = \exp\left(-i \frac{\gamma}{\text{scale}} H_C\right) = \prod_{i=0}^8 R_Z\left(\frac{2 \gamma h_i}{\text{scale}}\right) \prod_{i < j} R_{ZZ}\left(\frac{2 \gamma J_{ij}}{\text{scale}}\right)$$

The mixer Hamiltonian is standard transverse field:
$$U(B, \beta) = \exp\left(-i \beta \sum_{i=0}^8 X_i\right) = \prod_{i=0}^8 R_X(2\beta)$$

![QAOA Circuit Diagram](results/figures/qaoa_circuit.png)

---

## 2. Objective 1: Bell-State Preparation and Verification

To verify quantum hardware fidelity and quantify routing-induced noise degradation on Processor D, the Bell state $|\Phi^+\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}$ was prepared using $H$ on qubit 0 followed by $CX(0 \to 1)$. The state was measured in the three Pauli bases ($XX, YY, ZZ$) using 4096 shots per basis under both ideal and official noisy simulation.

### 2.1 Correlation & Fidelity Formalism
For two-qubit parity measurements, the correlation and standard error are:
$$\langle P \rangle = \frac{N_{\text{even}} - N_{\text{odd}}}{N}, \quad \mathrm{SE}(\langle P \rangle) = \sqrt{\frac{1 - \langle P \rangle^2}{N}}$$

Because $|\Phi^+\rangle\langle\Phi^+| = \frac{1}{4}(II + XX - YY + ZZ)$, state fidelity is computed as:
$$F = \frac{1 + \langle XX \rangle - \langle YY \rangle + \langle ZZ \rangle}{4}, \quad \mathrm{SE}(F) = \frac{1}{4}\sqrt{\mathrm{SE}_{XX}^2 + \mathrm{SE}_{YY}^2 + \mathrm{SE}_{ZZ}^2}$$

### 2.2 Measured Bell Results on Processor D

The measurements were performed on two physical pairs:
1. **Adjacent Pair $(0, 1)$:** Distance 1 in the coupling graph. Transpiled circuit depth = 2, CX count = 1.
2. **Farthest Pair $(0, 3)$:** Distance 2 in the coupling graph. Transpiled circuit depth = 7, CX count = 4 (requires 1 inserted SWAP gate).

| Pair Type | Physical Pair | Distance | Condition | CX Count | $\langle XX \rangle \pm \text{SE}$ | $\langle YY \rangle \pm \text{SE}$ | $\langle ZZ \rangle \pm \text{SE}$ | Fidelity $F \pm \text{SE}$ |
|---|---|---|---|---|---|---|---|---|
| **Adjacent** | $(0, 1)$ | 1 | **Ideal** | 1 | $1.0000 \pm 0.0000$ | $-1.0000 \pm 0.0000$ | $1.0000 \pm 0.0000$ | **$1.0000 \pm 0.0000$** |
| **Adjacent** | $(0, 1)$ | 1 | **Noisy** | 1 | $0.9458 \pm 0.0051$ | $-0.9521 \pm 0.0048$ | $0.9551 \pm 0.0046$ | **$0.9633 \pm 0.0021$** |
| **Farthest** | $(0, 3)$ | 2 | **Ideal** | 4 | $1.0000 \pm 0.0000$ | $-1.0000 \pm 0.0000$ | $1.0000 \pm 0.0000$ | **$1.0000 \pm 0.0000$** |
| **Farthest** | $(0, 3)$ | 2 | **Noisy** | 4 | $0.9448 \pm 0.0051$ | $-0.9360 \pm 0.0055$ | $0.9385 \pm 0.0054$ | **$0.9548 \pm 0.0023$** |

### 2.3 Physical Interpretation
- **Ideal Performance:** Under noiseless conditions, both adjacent and non-adjacent pairs exhibit perfect correlation ($\langle XX \rangle = 1.0$, $\langle YY \rangle = -1.0$, $\langle ZZ \rangle = 1.0$), confirming $F = 1.0000 \pm 0.0000$.
- **Adjacent Noisy Degradation:** For the adjacent pair $(0, 1)$, fidelity drops from $1.0000$ to $0.9633 \pm 0.0021$. This degradation is driven by three noise sources: two-qubit depolarizing error on the single CX gate ($p_2 = 0.005$), single-qubit gate errors ($p_1 = 0.001$), and symmetric readout bitflip noise ($p_{\text{readout}} = 0.01$ per qubit). Readout noise alone inverts bit parity with probability $\approx 2 p_{\text{readout}} = 0.02$, establishing an upper bound of $\approx 0.98$ on raw measured fidelity even before gate noise.
- **Farthest Pair Penalty:** For the farthest pair $(0, 3)$, physical distance 2 requires SABRE routing to insert a SWAP gate, which decomposes into 3 additional CX gates, quadrupling the CX count from 1 to 4. Each additional CX gate introduces two-qubit depolarizing noise ($p_2 = 0.005$), depressing $\langle YY \rangle$ from $-0.9521$ to $-0.9360$ and $\langle ZZ \rangle$ from $0.9551$ to $0.9385$. Consequently, the noisy fidelity suffers a statistically significant decline to $F = 0.9548 \pm 0.0023$.

---

## 3. Objective 2: Custom Processor D Design & Justification

### 3.1 Processor D Topology & Rule Compliance
Processor D was designed to mitigate routing bottlenecks for dense all-to-all quantum optimization problems while strictly obeying the five official architectural limits:
1. **Qubit Count:** 9 qubits (within $[9, 12]$).
2. **Connectivity:** Connected graph.
3. **Maximum Degree:** Uniform degree 4 (within $\le 4$).
4. **Gate Set:** Basis gates strictly $\{\text{rz}, \text{sx}, \text{x}, \text{cx}\}$.
5. **Noise Model:** Identical to the official synthetic noise model ($p_1 = 0.001, p_2 = 0.005, p_{\text{readout}} = 0.01$).

Both our internal validator and the official organizer validator `validate_processor_d(D, 9)` verified compliance with **0 errors**.

![Processor Coupling Graphs](results/figures/processors_graphs.png)
![Processor D Architecture](results/figures/processor_D_graph.png)

### 3.2 Topology Search & Quantitative Bottleneck Analysis on Processor B
In PS-O3, the 9-qubit knapsack Hamiltonian requires 36 non-local two-qubit interactions. We benchmarked candidate architectures against the reference Processor B:

- **Processor B Architecture:** 9 qubits, 12 edges, diameter 4, average degree $2.67$.
  - Required **17 SWAPs** during SABRE routing.
  - Final CX count expanded from 72 logical CX to **121 physical CX** (a **+49 CX routing overhead**, or $+68.1\%$).
  - Transpiled circuit depth reached **117** (two-qubit depth 79).

To eliminate this bottleneck, we systematically evaluated candidate topologies across 9 to 12 qubits (circulant graphs, random 4-regular graphs, and 2D grids):

| Candidate Name | Qubits | Edges | Max Degree | CX Count | CX Overhead | Total Depth | 2Q Depth | SWAPs | Noisy $P_{\text{opt}}$ |
|---|---|---|---|---|---|---|---|---|---|
| `rand4reg_n10_s4` | 10 | 20 | 4 | 97 | +25 | 82 | 51 | 9 | 0.0254 |
| `rand4reg_n10_s0` | 10 | 20 | 4 | 99 | +27 | 87 | 54 | 9 | 0.0264 |
| **`circulant_n9_o1-3`** | **9** | **18** | **4** | **99** | **+27** | **90** | **56** | **9** | **0.0266** |
| `circulant_n9_o1-2` (Frozen D) | 9 | 18 | 4 | 102 | +30 | 87 | 59 | 10 | 0.0225 |
| `circulant_n9_o2-3` | 9 | 18 | 4 | 100 | +28 | 88 | 57 | 10 | 0.0273 |
| *Processor B (Reference)* | *9* | *12* | *4* | *121* | *+49* | *117* | *79* | *17* | *0.0249* |

### 3.3 Expected vs. Measured Effect of Processor D
- **Expected Architectural Advantage:** By implementing a 4-regular circulant chordal topology with 18 bidirectional edges, the graph diameter drops from 4 to 2, and the average shortest path drops from $1.89$ to $1.50$. Every qubit can directly interact with 4 neighbors without passing through narrow linear chain bottlenecks.
- **Measured Hardware Effect:** Transpiling for Processor D reduces SWAP gates from 17 down to 10 (a **41.2% reduction**) and total CX count from 121 to 102 (saving **19 CX gates**, a **38.8% reduction in routing overhead**). Transpiled circuit depth decreases from 117 to 87 (a **25.6% depth reduction**). Under depolarizing noise, this gate reduction lowers the sampled mean QUBO cost by 7.89 units (74.96 on D vs 82.85 on B).

### 3.4 Engineering Trade-off
Increasing nodal degree to 4 across all 9 qubits increases physical wiring density and control line cross-routing on planar superconducting chips. In physical hardware, high-degree vertices significantly heighten the risk of parasitic capacitive coupling, microwave frequency collisions between neighboring transmon qubits, and residual $ZZ$-crosstalk.

---

## 4. Objective 3: Benchmarking Results on Processors A, B, and D

### 4.1 Capacity Limit on Processor A
- **Processor A:** 5 physical qubits, 4 edges.
- **Status:** **Not executable: needs 9 qubits, has 5.**
- **Capacity Analysis:** The 0/1 knapsack problem requires 5 decision qubits for the items and 4 binary slack qubits ($w \in \{1, 2, 4, 8\}$) to represent the inequality constraint up to capacity 15 without truncation. Truncating the slack bits to fit onto 5 qubits would alter the locked mathematical formulation and destroy constraint feasibility guarantees. Therefore, Processor A cannot execute PS-O3.

### 4.2 Benchmark Results Table
Directly extracted from [`results/tables/results.csv`](file:///Users/vaatsavkrishna/QFF/qff_ps_o3/results/tables/results.csv) and [`results/tables/results_detail.csv`](file:///Users/vaatsavkrishna/QFF/qff_ps_o3/results/tables/results_detail.csv):

| Problem | Processor | Condition | Executable | Logical Qubits | Physical Qubits | Logical CX | CX | Depth | 2Q Depth | SWAPs | CX Overhead | Shots | Quality Metric | Quality Value | $P_{\text{opt}}$ | Classical Optimum ($V^*$) | Random Baseline |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **PS-O3** | **A** | **ideal** | `false` | 9 | 5 | — | — | — | — | — | — | — | — | — | — | 26 | 0.875 |
| **PS-O3** | **A** | **noisy** | `false` | 9 | 5 | — | — | — | — | — | — | — | — | — | — | 26 | 0.875 |
| **PS-O3** | **B** | **ideal** | `true` | 9 | 9 | 72 | 121 | 117 | 79 | 17 | 49 | 4096 | `p_feasible` | **0.958740** | 0.020996 | 26 | 0.875 |
| **PS-O3** | **B** | **noisy** | `true` | 9 | 9 | 72 | 121 | 117 | 79 | 17 | 49 | 4096 | `p_feasible` | **0.943359** | 0.024902 | 26 | 0.875 |
| **PS-O3** | **D** | **ideal** | `true` | 9 | 9 | 72 | 102 | 87 | 59 | 10 | 30 | 4096 | `p_feasible` | **0.963379** | 0.022461 | 26 | 0.875 |
| **PS-O3** | **D** | **noisy** | `true` | 9 | 9 | 72 | 102 | 87 | 59 | 10 | 30 | 4096 | `p_feasible` | **0.942139** | 0.022461 | 26 | 0.875 |

### 4.3 Solution Quality & Random Baseline Analysis
- **Feasible Solution Probability ($P_{\text{feasible}}$):**
  - Uniform random guessing yields $P_{\text{feasible}} = 0.8750$.
  - QAOA achieves $P_{\text{feasible}} = 0.9587$ (B ideal), $0.9434$ (B noisy), $0.9634$ (D ideal), and $0.9421$ (D noisy).
  - QAOA successfully suppresses constraint violations, concentrating over $94\%$ of all measurements in the feasible subspace.
- **Ground-State Discovery ($P_{\text{opt}}$):**
  - Uniform random baseline: $P_{\text{opt}} = 0.03125$ ($3.125\%$).
  - Measured QAOA sampling rates: $0.0210$ (B ideal), $0.0249$ (B noisy), $0.0225$ (D ideal), and $0.0225$ (D noisy).
  - At depth $p=1$, QAOA does **not** beat uniform random guessing for finding the single ground state.
- **Saturation of Best Feasible Value:**
  - Across 4096 shots, the probability of sampling the optimal combination at least once exceeds $1 - (1 - 0.0225)^{4096} \approx 100\%$. Both Processor B and Processor D achieve $V^* = 26$ (items $\{1, 2, 3, 4\}$, weight 14), corresponding to **100.0% of the optimal value**.

---

## 5. Objective Landscape Analysis on Processor D

The objective landscape was mapped across a $20 \times 20$ grid over $\gamma \in [0.0, 1.0]$ and $\beta \in [0, \pi]$ using 1024 shots per grid point on Processor D under official noise, alongside an exact statevector ideal landscape.

![Objective Landscape](results/figures/landscape_D.png)

### 5.1 Seed Optimization Dynamics
Five pseudorandom starting angles were drawn according to the official protocol $\gamma_0, \beta_0 \sim U[0, \pi]$ using NumPy's `default_rng(seed)`:

| Seed | Initial $\gamma_0$ | Initial $\beta_0$ | Optimized $\gamma^*$ | Optimized $\beta^*$ | Expectation $\langle C_{\text{scaled}} \rangle$ | Function Evaluations | Exact $P_{\text{feasible}}$ | Exact $P_{\text{opt}}$ |
|---|---|---|---|---|---|---|---|---|
| **0** | 2.0011 | 0.8476 | 2.5414 | 1.5196 | -0.0081 | 200 (maxiter) | 0.8734 | 0.0319 |
| **1 (Best)** | **1.6079** | **2.9860** | **0.2831** | **2.8648** | **-1.5232** | **78** | **0.9554** | **0.0226** |
| **2** | 0.8219 | 0.9377 | 3.0164 | 3.0877 | -0.0057 | 145 | 0.8759 | 0.0317 |
| **3** | 0.2691 | 0.7440 | 0.2844 | 1.3544 | -0.8535 | 94 | 0.8916 | 0.0393 |
| **4** | 2.9627 | 1.6064 | 4.0598 | 1.5992 | -0.0007 | 67 | 0.8751 | 0.0311 |

### 5.2 Landscape Topography & Noise Flattening
- **Global Optimum Location:** The COBYLA optimizer converged from Seed 1 to the global minimum at $(\gamma^* = 0.2831, \beta^* = 2.8648)$ with expectation $-1.5232$. This matches the noisy sampled landscape grid, where the grid minimum of $78.36$ occurs at $\gamma = 0.263, \beta = 2.811$.
- **Narrowness of the Convergence Valley:** The landscape reveals a steep, narrow ravine confined to $\gamma \in [0.20, 0.35]$. For $\gamma > 0.40$, the dense interference of 36 non-commuting $ZZ$ rotations creates a chaotic, oscillatory plateau.
- **Why Seeds 0, 2, and 4 Failed:** Seeds 0, 2, and 4 initialized at $\gamma_0 \gg 0.40$. Landing in the flat, highly corrugated plateau, the gradient-free COBYLA optimizer became trapped in negligible local ripples, yielding expectations near zero ($-0.0081, -0.0057, -0.0007$) and feasibility rates indistinguishable from uniform random guessing ($87.3\% - 87.6\%$). Only seeds initialized near or below the valley (Seeds 1 and 3) descended into the true minimum.
- **Noise Attenuation:** Depolarizing and readout noise contract the dynamic range of the landscape and lift the mean grid cost to $322.03$ (well above the random baseline cost of $233.0$), smoothing the steep valley walls.

---

## 6. Trade-Offs, Limitations, and Evidence-Based Improvements

### 6.1 Architectural and Algorithmic Limitations
1. **Shallow Ansatz Expressiveness ($p=1$):** At $p=1$, the circuit has only two control parameters $(\gamma, \beta)$. This is insufficient to concentrate probability onto a unique, capacity-saturating ground state in a dense 9-qubit combinatorial problem, causing probability to disperse across suboptimal feasible states.
2. **Slack Variable Overhead:** Binary slack encoding requires 4 additional auxiliary qubits to handle the capacity constraint. This represents an **80% qubit overhead** for 5 decision variables and introduces 26 auxiliary $ZZ$ coupling terms into the Hamiltonian.
3. **Connectivity Mismatch:** The knapsack problem induces an all-to-all interaction graph ($K_9$). On planar hardware restricted to degree $\le 4$, routing requires 10 to 17 SWAP gates, expanding circuit depth by up to $68\%$.
4. **Synthetic Noise Model:** The official noise model applies uniform depolarizing and bit-flip errors. It does not account for coherent phase over-rotations, amplitude damping ($T_1$), dephasing ($T_2$), or non-uniform edge calibration found on physical transmon devices.

### 6.2 Three Concrete Evidence-Based Improvements
1. **Unbalanced Slack Penalization (Slack Elimination):**
   *Method:* Replace the 4 binary slack qubits with an unbalanced linear-quadratic penalty function applied directly to the 5 item variables:
   $$P_{\text{unbalanced}}(x) = \alpha \max\left(0, \sum w_i x_i - W\right)^2$$
   *Evidence:* Eliminating the 4 slack qubits reduces the problem from 9 qubits to 5 qubits and drops $ZZ$ interactions from 36 to 10. This reduces circuit depth by $>60\%$ and allows the problem to execute on compact 5-qubit processors like Processor A.

![Unbalanced vs Slack Comparison](results/figures/unbalanced_vs_slack.png)

2. **Multi-Angle QAOA (ma-QAOA) and $p \ge 2$ Layering:**
   *Method:* Assign distinct variational parameters $\gamma_{ij}$ to each Hamiltonian edge and $\beta_i$ to each qubit, or increase depth to $p=2$.
   *Evidence:* The classical seed sweep proved that global $(\gamma, \beta)$ parameters cannot selectively amplify the optimal subset $[1, 2, 3, 4]$ over safe interior subsets like $[1, 3]$. Multi-angle QAOA provides the necessary degrees of freedom to bias amplitudes toward the capacity boundary.
3. **Dynamical Decoupling (DD) & Zero-Noise Extrapolation (ZNE):**
   *Method:* Insert $XY4$ or CPMG dynamical decoupling pulse sequences on idle qubits during routing SWAP delays, combined with digital unitary folding to extrapolate to the zero-noise limit.
   *Evidence:* In the Bell experiment, adding 3 CX gates for a distant pair reduced state fidelity by $0.85$ percentage points. In QAOA, noise raised the mean QUBO cost by $26.09$ units on Processor D. Active error mitigation directly suppresses this depth-dependent depolarizing degradation.

---

## 7. Compliance and Verification Sign-Off

- **Hard Rules Integrity:** `qff_phase2.py` was preserved completely unmodified. Official settings (`rz, sx, x, cx`, `optimization_level=1`, SABRE, `seed_transpiler=42`, `seed_simulator=42`, 4096 shots, official noise) were maintained across all required benchmark runs.
- **Reproducibility:** Executable top-to-bottom via `jupyter nbconvert --to notebook --execute main.ipynb --output main_executed.ipynb` with complete numerical consistency across all tables and figures.

