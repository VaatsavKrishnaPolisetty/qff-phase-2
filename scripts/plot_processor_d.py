#!/usr/bin/env python3
"""Generate high-resolution visualization for Processor D (4-regular circulant C_9(1, 2))."""

from pathlib import Path
import json
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

def generate_processor_d_figure():
    root = Path(__file__).resolve().parent.parent
    proc_path = root / "processors" / "processor_D.json"
    out_path = root / "results" / "figures" / "processor_D_graph.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(proc_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    edges = data["edges"]
    g = nx.Graph()
    g.add_nodes_from(range(9))
    g.add_edges_from(edges)

    fig, ax = plt.subplots(figsize=(8.5, 8.5), dpi=300)
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")

    # Circular layout
    pos = nx.circular_layout(g)

    # Classify edges into ring (distance 1) and chord (distance 2)
    ring_edges = []
    chord_edges = []
    for u, v in g.edges():
        diff = abs(u - v)
        cyclic_dist = min(diff, 9 - diff)
        if cyclic_dist == 1:
            ring_edges.append((u, v))
        elif cyclic_dist == 2:
            chord_edges.append((u, v))

    # Draw chord edges (offset 2)
    nx.draw_networkx_edges(
        g, pos, edgelist=chord_edges,
        edge_color="#6366f1", width=2.4, alpha=0.85,
        ax=ax, label="Chord Couplings: (i \u00b1 2 mod 9) [9 edges]"
    )

    # Draw ring edges (offset 1)
    nx.draw_networkx_edges(
        g, pos, edgelist=ring_edges,
        edge_color="#0284c7", width=3.0, alpha=0.95,
        ax=ax, label="Ring Couplings: (i \u00b1 1 mod 9) [9 edges]"
    )

    # Draw nodes
    nx.draw_networkx_nodes(
        g, pos,
        node_color="#f0f9ff",
        edgecolors="#0369a1",
        linewidths=2.5,
        node_size=1100,
        ax=ax
    )

    # Labels
    labels = {i: f"$q_{i}$" for i in range(9)}
    nx.draw_networkx_labels(
        g, pos, labels=labels,
        font_size=13, font_family="sans-serif", font_weight="bold",
        font_color="#0f172a", ax=ax
    )

    ax.set_title(
        r"$\mathbf{Processor\ D\ Architecture:\ 4-Regular\ Circulant\ Graph\ C_9(1, 2)}$",
        fontsize=14, pad=22, color="#0f172a"
    )

    subtitle = "9 Qubits | 18 Bidirectional Edges | Uniform Degree 4 | Diameter 2 | Avg Path Length: 1.50\n(Bell Analysis: Pair (0,1) is Adjacent [dist 1]; Pair (0,3) is Farthest [dist 2 via q1 or q2])"
    ax.text(
        0.5, 1.02, subtitle,
        transform=ax.transAxes, ha="center", va="bottom",
        fontsize=9.5, color="#475569", linespacing=1.3
    )

    ax.legend(
        loc="lower center", bbox_to_anchor=(0.5, -0.07),
        ncol=2, frameon=True, facecolor="#f8fafc", edgecolor="#cbd5e1",
        fontsize=9.5
    )

    ax.axis("off")
    fig.subplots_adjust(top=0.88, bottom=0.1)
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Successfully rendered Processor D C_9(1,2) figure to: {out_path}")

if __name__ == "__main__":
    generate_processor_d_figure()
