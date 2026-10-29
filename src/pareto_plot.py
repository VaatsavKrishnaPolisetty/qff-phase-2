"""Generate the Pareto Trade-Off Plot for Processor D hardware topology exploration.

Plots CX gate count (execution overhead) vs. Number of Edges (coupling / chip cost proxy),
labeling candidate layouts (rings, degree-3 grids, 10-12 qubit layouts, circulants, random 4-regular),
drawing the Pareto frontier, and highlighting the design choice (Processor D: circulant_n9_o1-2).
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def generate_pareto_plot(
    csv_path: Path = None,
    output_fig: Path = None,
    output_csv: Path = None,
):
    root_dir = Path(__file__).resolve().parent.parent
    if csv_path is None:
        csv_path = root_dir / "results/tables/d_search.csv"
    if output_fig is None:
        output_fig = root_dir / "results/figures/pareto_design_d.png"
    if output_csv is None:
        output_csv = root_dir / "results/extra/pareto_candidates.csv"

    df = pd.read_csv(csv_path)

    # Identify Pareto frontier (minimizing n_edges and minimizing cx)
    pareto_mask = []
    for idx, row in df.iterrows():
        dominated = False
        for jdx, other in df.iterrows():
            if (other['n_edges'] <= row['n_edges'] and other['cx'] <= row['cx']) and \
               (other['n_edges'] < row['n_edges'] or other['cx'] < row['cx']):
                dominated = True
                break
        pareto_mask.append(not dominated)

    df['pareto_optimal'] = pareto_mask
    df_sorted = df.sort_values(by=['pareto_optimal', 'cx', 'n_edges'], ascending=[False, True, True])

    # Save summary table of candidates and Pareto status
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"Saved candidate Pareto dataset to {output_csv}")

    # Configure plotting style
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.size': 11,
        'axes.labelsize': 13,
        'axes.titlesize': 14,
        'legend.fontsize': 10,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'figure.autolayout': True,
        'grid.alpha': 0.4,
        'grid.linestyle': '--'
    })

    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=200)

    # Classify layout candidates
    rings = df[df['name'].str.startswith('ring_')]
    deg3_grids = df[df['name'].isin(['grid_2x5'])]
    deg4_grids = df[df['name'].isin(['grid_3x3', 'grid_3x4'])]
    proc_b = df[df['name'] == 'PROCESSOR_B (reference)']
    circ_n9 = df[df['name'].str.startswith('circulant_n9_') & (df['name'] != 'circulant_n9_o1-2')]
    rand4_n9 = df[df['name'].str.startswith('rand4reg_n9_')]
    larger_qubits = df[df['num_qubits'] > 9]
    proc_d = df[df['name'] == 'circulant_n9_o1-2'].iloc[0]

    # Plot scatter groups
    ax.scatter(rings['n_edges'], rings['cx'], color='#7f7f7f', marker='o', s=80, alpha=0.7, label='Rings (Degree-2, 9-12Q)', zorder=3)
    ax.scatter(deg3_grids['n_edges'], deg3_grids['cx'], color='#ff7f0e', marker='^', s=100, alpha=0.9, label='Degree-3 Planar (grid_2x5, 10Q)', zorder=3)
    ax.scatter(deg4_grids['n_edges'], deg4_grids['cx'], color='#e377c2', marker='D', s=70, alpha=0.7, label='Planar Grids (grid_3x3, grid_3x4)', zorder=3)
    ax.scatter(larger_qubits['n_edges'], larger_qubits['cx'], color='#1f77b4', marker='s', s=70, alpha=0.6, label='10-12 Qubit Variants (Routing Slack)', zorder=3)
    ax.scatter(circ_n9['n_edges'], circ_n9['cx'], color='#2ca02c', marker='v', s=80, alpha=0.8, label='Circulant Candidates (9Q, Deg-4)', zorder=3)
    ax.scatter(rand4_n9['n_edges'], rand4_n9['cx'], color='#17becf', marker='p', s=70, alpha=0.6, label='Random 4-Regular (9Q)', zorder=3)
    ax.scatter(proc_b['n_edges'], proc_b['cx'], color='#9467bd', marker='X', s=140, edgecolor='black', linewidth=1.5, label='Processor B (Official, 12 edges, 121 CX)', zorder=4)

    # Highlight Pareto frontier
    pareto_df = df[df['pareto_optimal']].sort_values('n_edges')
    ax.plot(pareto_df['n_edges'], pareto_df['cx'], color='#d62728', linestyle='--', linewidth=2, alpha=0.85, label='Pareto Frontier (Cost vs Routing Overhead)', zorder=2)
    ax.scatter(pareto_df['n_edges'], pareto_df['cx'], facecolors='none', edgecolors='#d62728', s=180, linewidth=2, zorder=5)

    # Mark Selected Processor D
    ax.scatter([proc_d['n_edges']], [proc_d['cx']], color='#d62728', edgecolors='black', marker='*', s=350, linewidth=1.8, label='Selected: Processor D (circulant_n9_o1-2)', zorder=6)

    # Annotate key designs
    annotations = [
        ('ring_n9', 'ring_n9 (146 CX)', (-15, 10)),
        ('grid_2x5', 'grid_2x5 [deg-3] (116 CX)', (10, 8)),
        ('grid_3x3', 'grid_3x3 (117 CX)', (-70, -18)),
        ('PROCESSOR_B (reference)', 'Processor B (121 CX)', (10, 10)),
        ('circulant_n9_o1-3', 'circulant_n9_o1-3 (99 CX)', (-120, -15)),
        ('rand4reg_n10_s4', 'rand4reg_n10_s4 (97 CX)', (10, -10)),
        ('rand4reg_n12_s1', 'rand4reg_n12_s1 [12Q] (99 CX)', (10, 5)),
        ('circulant_n9_o1-2', 'Processor D Choice\n(18 edges, 102 CX, Depth 87)', (15, -25))
    ]

    for name, text, offset in annotations:
        match = df[df['name'] == name]
        if not match.empty:
            row = match.iloc[0]
            ax.annotate(
                text,
                xy=(row['n_edges'], row['cx']),
                xytext=(row['n_edges'] + offset[0]*0.05, row['cx'] + offset[1]*0.6),
                arrowprops=dict(arrowstyle="->", color="black", lw=0.9, shrinkA=3, shrinkB=3),
                fontsize=8.5,
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="gray", alpha=0.85, lw=0.5),
                zorder=7
            )

    ax.set_xlabel("Number of Coupling Edges (Proxy for Chip Hardware Cost / Routing Complexity)")
    ax.set_ylabel("Compiled CX Gate Count (QAOA p=1 on 9-Qubit QUBO)")
    ax.set_title("Architecture Trade-Off Analysis: Pareto Frontier for Processor D Design", fontweight='bold', pad=12)
    ax.set_xlim(7.5, 25.5)
    ax.set_ylim(90, 175)
    ax.grid(True)
    ax.legend(loc='upper right', framealpha=0.95, edgecolor='gray', shadow=True)

    output_fig.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_fig, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Generated Pareto plot saved to {output_fig}")

if __name__ == "__main__":
    generate_pareto_plot()
