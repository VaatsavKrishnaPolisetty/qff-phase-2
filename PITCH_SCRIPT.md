# 3-Minute Presentation Pitch & Defense Script
## QFF 2026 Phase 2 — Problem Statement PS-O3
### Team: Emerging Genius

---

### Timer Breakdown (180 Seconds Total)
* **0:00 – 0:35:** The Hook & The Problem (Knapsack & QUBO)
* **0:35 – 1:10:** The Hardware Bottleneck & Our Custom Processor D
* **1:10 – 1:50:** Key Benchmark Results & Bell-State Physics
* **1:50 – 2:30:** High-Impact Extensions (Slack Elimination & ZNE)
* **2:30 – 3:00:** Conclusion & Call for Questions

---

### Pitch Delivery Script

#### [0:00 - 0:35] Slide 1: The Problem & Mathematical Formulation
> "Hello judges, we are team **Emerging Genius**, presenting our quantum optimization solution for **Problem Statement PS-O3: Resource-Constrained Item Selection (0/1 Knapsack)**.
>
> In real-world cargo logistics, portfolio management, and cloud scheduling, allocating items under a strict budget constraint is NP-hard. Classical computers can solve 5 items in milliseconds, but at 100 items, classical brute-force would take longer than the age of the universe.
>
> We translated the locked 5-item, 15-capacity instance into a **9-qubit Quadratic Unconstrained Binary Optimization (QUBO)** model using an exact 4-qubit binary slack encoding ($s \in \{0 \dots 15\}$) and a quadratic penalty multiplier $P = 5$. Our formulation was mathematically verified across all 512 bitstrings against classical exhaustive search, confirming the exact global ground state at **$V^* = 26$** (items 1, 2, 3, and 4; weight 14)."

---

#### [0:35 - 1:10] Slide 2: The Routing Bottleneck & Our Processor D Architecture
> "When mapping the resulting 36-term dense Ising Hamiltonian onto physical quantum chips, we uncovered a critical hardware routing bottleneck on the organizer's reference **Processor B** (9 qubits, 12 edges, diameter 4). Because of its sparse connectivity, SABRE routing was forced to insert **17 SWAP gates**, inflating two-qubit gate count to **121 CX gates**—an unsustainable **+68% CX overhead**—and stretching circuit depth to 117.
>
> To solve this, we architected **Processor D**, an elegant 4-regular circulant chordal ring topology ($C_9(1, 2)$) with 18 bidirectional coupling edges that strictly passes all official rules (degree $\le 4$, connected, standard basis). 
>
> By collapsing the chip diameter from 4 to 2, Processor D cuts routing SWAPs by **$41.2\%$** (from 17 down to 10), saves 19 physical CX gates, and compresses circuit depth by **$25.6\%$** (down to 87)."

---

#### [1:10 - 1:50] Slide 3: Benchmark Findings & Bell-State Verification
> "Under the official synthetic noise model (depolarizing and readout bit-flips), we benchmarked Processors A, B, and D with 4096 shots:
> 1. **Processor A (5 qubits):** Evaluated as strictly **not executable** under the capacity rule, as the locked 9-qubit model requires 5 decision + 4 slack qubits.
> 2. **Feasibility:** QAOA at $p=1$ decisively outperformed uniform random guessing ($87.50\%$), concentrating **$94.21\%$** of samples on Processor D into the feasible subspace and capturing **$100.0\%$** of the optimal classical value ($V^* = 26$).
> 3. **Objective 1 Bell State:** We prepared the $|\Phi^+\rangle$ state on Processor D. On the adjacent pair, noisy fidelity reached **$0.9633 \pm 0.0021$**. On the distant pair, routing inserted a SWAP gate, quadrupling the CX count from 1 to 4 and causing a statistically significant drop to **$0.9548 \pm 0.0023$**, proving directly how routing density degrades quantum fidelity."

---

#### [1:50 - 2:30] Slide 4: Beyond the Required Benchmark — Breakthrough Extensions
> "We went beyond the required benchmark with three evidence-based experiments:
> 1. **Slack Elimination via Unbalanced Penalization:** By removing the 4 slack qubits and tuning an unbalanced quadratic barrier directly on 5 qubits, we solved the Processor A capacity limit! The circuit now executes on Processor A in just 32 CX gates, and on Processor B in only 26 CX gates (a **$78.5\%$ gate reduction**). Crucially, this doubled ground-state discovery rate ($P_{\text{opt}}$) from $2.2\%$ to **$6.3\%$**, beating uniform random guessing by almost $2\times$!
> 2. **Depth $p=2$ QAOA:** Doubled variational control, pushing feasible sampling to **$96.85\%$**.
> 3. **Zero-Noise Extrapolation (ZNE):** Applied digital unitary folding ($\lambda \in \{1, 3, 5\}$) to extrapolate back to zero noise, successfully recovering 13.4 units of mean QUBO cost degradation."

---

#### [2:30 - 3:00] Conclusion & Opening for Q&A
> "In summary, our project demonstrates a complete, mathematically verified, reproducible quantum workflow: from QUBO formulation to custom chip design, noise characterization, and error mitigation. All results run in under 30 seconds and match our submitted report with zero discrepancies.
>
> Thank you, and we welcome your questions!"

---

### Anticipated Judge Questions & Bulletproof Answers

#### Q1: "Why did QAOA at $p=1$ beat random guessing on feasibility ($94.2\%$ vs $87.5\%$), but not on finding the exact optimal subset ($2.2\%$ vs $3.1\%$)?
* **Answer:** *"In the QUBO objective, the quadratic penalty $P=5$ penalizes constraint violations heavily (by $+5, +20, +45 \dots$), while value differences among valid subsets are small (0 to 26). At shallow depth $p=1$, the optimizer's two global angles $(\gamma, \beta)$ rapidly lower energy by evacuating probability mass out of the 4 invalid states into the 28 valid states. But because the valid subspace is flat and broad, probability spreads across safe interior solutions rather than concentrating on the single boundary-tight optimum. That is why our Additional Experiment with Unbalanced Penalization was so crucial—it doubled $P_{\text{opt}}$ to $6.3\%$ by removing the slack subspace dispersion."*

#### Q2: "Why couldn't you run PS-O3 on Processor A?"
* **Answer:** *"Processor A has only 5 qubits. PS-O3 has 5 items plus 4 binary slack variables needed to represent the capacity inequality up to 15 without truncation. Dropping slack bits on the required benchmark would violate the locked problem statement. However, in our Additional Experiment (Section 12), we proved that an unbalanced penalty formulation fits completely within Processor A's 5 qubits and achieves an optimal state discovery rate of $5.2\%$ under official noise."*

#### Q3: "What is the physical engineering trade-off of your Processor D design?"
* **Answer:** *"While our 4-regular circulant graph reduces graph diameter from 4 to 2 and cuts SWAPs by $41\%$, increasing the degree of every qubit to 4 creates physical wiring density challenges on planar superconducting transmon chips. More adjacent control lines increase parasitic capacitive coupling, microwave frequency allocation collision risks, and residual $ZZ$-crosstalk."*

